"""기프트클린 네이버 블로그 작성 도우미 — 로컬 웹 서버 (FastAPI).

이 서버는 항상 127.0.0.1(localhost)에서만 열리며, 단일 사용자 로컬 앱 전제로
CORS를 전체 허용한다(외부에 노출하지 않는다는 전제 — config/safety.py 참고).

엔드포인트:
  GET  /                          → 웹 UI
  GET  /api/status                → 환경(.env) + 안전설정 점검 (비밀값은 절대 노출 안 함)
  POST /api/keywords/research     → 키워드 후보 확장 + 실데이터 조회 + 점수화
  POST /api/generate              → 기프트클린 글 생성 (승인된 키워드 반영) + 개인정보 경고
  POST /api/publish               → 임시저장 실행 (DRY_RUN이면 실제 네이버 접촉 없이 미리보기만)
  GET  /api/progress/{job_id}     → 임시저장 진행상황 SSE
"""
from __future__ import annotations

import base64
import json
import logging
import queue
import sys
import threading
import uuid
from pathlib import Path
from typing import Optional

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from utils.env_loader import EnvConfig
from utils.logger import setup_logger
from utils.mask import mask_secrets
import config.safety as safety
from core import pii_guard
from core.image_exif import strip_gps
from models.giftclean_post import (
    GiftCleanPostRequest, ServiceType, PhotoGroup,
)
from core.keyword_research import KeywordResearchService
from core.giftclean_writer import GiftCleanWriter

setup_logger()
logger = logging.getLogger("web.server")

STATIC_DIR = PROJECT_ROOT / "web" / "static"
UPLOAD_TMP_DIR = PROJECT_ROOT / "eval" / "_tmp_photos"

app = FastAPI(title="기프트클린 블로그 작성 도우미")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # 로컬 단일 사용자 전제(요청사항: localhost 외부 접속은 서버 bind 단계에서 차단)
    allow_methods=["*"],
    allow_headers=["*"],
)

try:
    ENV = EnvConfig()
except Exception as exc:
    logger.warning(f"EnvConfig 경고: {mask_secrets(str(exc))}")
    ENV = None

JOBS: dict[str, dict] = {}


# ─────────────────────────────────────────────────────────────────
# 요청 모델
# ─────────────────────────────────────────────────────────────────
class KeywordResearchIn(BaseModel):
    service_type: ServiceType
    region: str
    topic: str
    extra_seeds: list[str] = Field(default_factory=list)


class SelectedKeywords(BaseModel):
    main: str = ""
    sub: list[str] = Field(default_factory=list)
    question: list[str] = Field(default_factory=list)
    region: list[str] = Field(default_factory=list)
    user_edited: bool = False


class GenerateIn(BaseModel):
    post: GiftCleanPostRequest
    keywords: SelectedKeywords


class PhotoOut(BaseModel):
    media_type: str = "image/jpeg"
    data: str
    filename: str = ""
    group: Optional[PhotoGroup] = None
    order: int = 0
    caption: str = ""
    strip_gps: bool = True


class PublishIn(BaseModel):
    title: str
    sections: list[dict] = Field(default_factory=list)
    tags: list[str] = Field(default_factory=list)
    photos: list[PhotoOut] = Field(default_factory=list)
    blog_id: str = ""
    confirmed: bool = False   # 사용자가 최종 확인 화면에서 눌러야 True


# ─────────────────────────────────────────────────────────────────
# 정적 / 상태
# ─────────────────────────────────────────────────────────────────
if STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


@app.get("/")
def index():
    idx = STATIC_DIR / "index.html"
    if not idx.exists():
        raise HTTPException(500, "index.html이 없습니다.")
    return FileResponse(str(idx), headers={"Cache-Control": "no-cache, no-store, must-revalidate"})


@app.get("/api/status")
def status():
    if ENV is None:
        return {
            "ok": False,
            "error": ".env 계정 정보가 없습니다 (NAVER_ID/PW/BLOG_ID 또는 USE_CHROME_PROFILE=true).",
            "dry_run": safety.DRY_RUN, "allow_publish": safety.ALLOW_PUBLISH,
        }
    return {
        "ok": True,
        "dry_run": safety.DRY_RUN,
        "allow_publish": safety.ALLOW_PUBLISH,  # 항상 False
        "naver_account": bool(ENV.naver_id) or ENV.use_chrome_profile,
        "use_chrome_profile": ENV.use_chrome_profile,
        "blog_id": ENV.blog_id or "",
        "claude": bool(ENV.claude_api_key),
        "openai": bool(ENV.openai_api_key),
        "searchad": bool(ENV.naver_searchad_api_key),
        "datalab": bool(ENV.naver_datalab_client_id),
        "max_image_mb": safety.MAX_IMAGE_SIZE_MB,
        "max_posts_per_run": safety.MAX_POSTS_PER_RUN,
    }


# ─────────────────────────────────────────────────────────────────
# 키워드 조사 (요청사항: AI 추측 전에 반드시 조사)
# ─────────────────────────────────────────────────────────────────
@app.post("/api/keywords/research")
def keywords_research(req: KeywordResearchIn):
    if ENV is None:
        raise HTTPException(400, ".env 설정이 없습니다.")
    svc = KeywordResearchService(ENV)
    try:
        result = svc.research(req.service_type, req.region.strip(), req.topic.strip(), req.extra_seeds)
        return result.to_dict()
    except Exception as exc:
        logger.exception("키워드 조사 실패")
        raise HTTPException(500, f"키워드 조사 실패: {mask_secrets(str(exc))}")


# ─────────────────────────────────────────────────────────────────
# 글 생성
# ─────────────────────────────────────────────────────────────────
@app.post("/api/generate")
def generate(req: GenerateIn):
    if ENV is None:
        raise HTTPException(400, ".env 설정이 없습니다.")

    # 입력값 자체의 문제(예: 작업사례형인데 사진이 없음)를 먼저 알려준다 —
    # API 키가 없어서 나는 오류와 사용자의 입력 실수를 구분해서 보여주기 위함.
    business_errors = req.post.validate_business_rules()
    if business_errors:
        raise HTTPException(400, "; ".join(business_errors))

    if not (ENV.claude_api_key or ENV.openai_api_key):
        raise HTTPException(400, "CLAUDE_API_KEY 또는 OPENAI_API_KEY가 .env에 없습니다.")

    provider = "claude" if ENV.claude_api_key else "openai"
    try:
        writer = GiftCleanWriter(
            provider=provider, claude_api_key=ENV.claude_api_key, openai_api_key=ENV.openai_api_key,
        )
        result = writer.generate(req.post, question_keywords=req.keywords.question)
    except Exception as exc:
        logger.exception("글 생성 실패")
        raise HTTPException(500, f"글 생성 실패: {mask_secrets(str(exc))}")

    filenames = [p.filename for p in req.post.photos if p.filename]
    pii = pii_guard.full_scan(body_text=result.body, memo=req.post.memo, filenames=filenames)

    # 요청사항 14번: 키워드 조사 기록에 작성된 글 제목까지 남긴다
    try:
        from core.keyword_research import KeywordResearchResult
        record = KeywordResearchResult(
            researched_at="", original_topic=req.post.topic, service=req.post.service_type.value,
            region=req.post.region, candidates=[], api_available=bool(ENV.naver_searchad_api_key),
            main_keyword=req.keywords.main, sub_keywords=req.keywords.sub,
            question_keywords=req.keywords.question, region_keywords=req.keywords.region,
            manual_mode=not bool(ENV.naver_searchad_api_key),
            user_edits=["사용자 승인/수정됨"] if req.keywords.user_edited else [],
        )
        KeywordResearchService.save_record(record, written_title=result.title)
    except Exception:
        logger.warning("키워드 조사 기록 저장 실패(비치명적)", exc_info=True)

    payload = result.model_dump()
    payload["pii_warning"] = {"has_warning": pii.has_warning, "findings": pii.findings}
    payload["manual_photo_checklist"] = pii_guard.MANUAL_PHOTO_CHECKLIST if req.post.photos else ""
    payload["dry_run"] = safety.DRY_RUN
    return payload


# ─────────────────────────────────────────────────────────────────
# 임시저장 (DRY_RUN이면 실제 네이버 접촉 없음)
# ─────────────────────────────────────────────────────────────────
@app.post("/api/publish")
def publish(req: PublishIn):
    if ENV is None:
        raise HTTPException(400, ".env 계정 정보가 없습니다.")
    if not req.confirmed:
        raise HTTPException(400, "최종 확인(제목/글자수/사진수/태그/개인정보 경고 확인) 후 다시 요청하세요.")
    if not req.sections and not req.title:
        raise HTTPException(400, "저장할 글 내용이 없습니다.")

    safety.enforce_single_post_run(1)  # 1회 실행당 최대 글 1개

    for p in req.photos:
        if p.filename and not safety.validate_image_extension(p.filename):
            raise HTTPException(400, f"허용되지 않는 이미지 확장자입니다: {p.filename}")
        approx_bytes = int(len(p.data) * 3 / 4)
        if not safety.validate_image_size(approx_bytes):
            raise HTTPException(400, f"이미지 용량 제한({safety.MAX_IMAGE_SIZE_MB}MB) 초과: {p.filename}")
    if len(req.photos) > safety.MAX_IMAGES_PER_POST:
        raise HTTPException(400, f"사진은 최대 {safety.MAX_IMAGES_PER_POST}장까지 가능합니다.")

    job_id = uuid.uuid4().hex[:12]
    JOBS[job_id] = {"q": queue.Queue(), "done": False}
    threading.Thread(target=_run_publish, args=(job_id, req), daemon=True).start()
    return {"job_id": job_id, "dry_run": safety.DRY_RUN}


@app.get("/api/progress/{job_id}")
def progress(job_id: str):
    job = JOBS.get(job_id)
    if job is None:
        raise HTTPException(404, "존재하지 않는 작업입니다.")

    def event_stream():
        q: queue.Queue = job["q"]
        while True:
            try:
                item = q.get(timeout=15)
            except queue.Empty:
                yield ": ping\n\n"
                if job["done"]:
                    break
                continue
            yield f"data: {json.dumps(item, ensure_ascii=False)}\n\n"
            if item.get("type") == "done":
                break
        JOBS.pop(job_id, None)

    return StreamingResponse(event_stream(), media_type="text/event-stream")


# ─────────────────────────────────────────────────────────────────
# 발행 워커
# ─────────────────────────────────────────────────────────────────
def _save_photo(p: PhotoOut, idx: int) -> str:
    """base64 사진을 임시 파일로 저장. strip_gps=True면 GPS EXIF를 제거한 '새 파일'로 저장한다
    (원본 base64/파일을 덮어쓰지 않는다)."""
    UPLOAD_TMP_DIR.mkdir(parents=True, exist_ok=True)
    raw = base64.b64decode(p.data)
    if p.strip_gps:
        raw = strip_gps(raw)
    ext = (p.media_type.split("/")[-1] or "jpg").replace("jpeg", "jpg")
    group_tag = (p.group.value if p.group else "photo").replace(" ", "")
    fp = UPLOAD_TMP_DIR / f"{idx:03d}_{group_tag}.{ext}"
    fp.write_bytes(raw)
    return str(fp)


def _run_publish(job_id: str, req: PublishIn):
    job = JOBS[job_id]
    q: queue.Queue = job["q"]

    def emit(step: str, pct: int):
        q.put({"type": "progress", "step": mask_secrets(step), "pct": pct})

    if safety.DRY_RUN:
        _run_dry_run(req, emit, q)
        job["done"] = True
        return

    orch = None
    try:
        from automation.orchestrator import PostingOrchestrator

        emit("사진을 준비하고 있어요...", 5)
        ordered = sorted(
            req.photos,
            key=lambda p: ({"작업 전": 0, "작업 중": 1, "작업 후": 2}.get(p.group.value if p.group else "", 9), p.order),
        )
        photo_plan = []
        for i, p in enumerate(ordered):
            local_path = _save_photo(p, i)
            photo_plan.append({
                "local_path": local_path,
                "group": p.group.value if p.group else "",
                "caption": p.caption,
            })

        blog_id = req.blog_id or ENV.blog_id
        orch = PostingOrchestrator(env_config=ENV, progress_callback=emit)

        emit("브라우저를 열고 네이버에 로그인 중...", 10)
        account = None
        if ENV.naver_id and ENV.naver_pw:
            account = {"id": ENV.naver_id, "pw": ENV.naver_pw, "blog_id": blog_id}
        if not orch.open_and_login(blog_id, account=account):
            raise RuntimeError("네이버 로그인 또는 에디터 진입에 실패했습니다. .env 계정 정보를 확인하세요.")

        ok_write = orch.write_content(req.title, req.sections, photo_plan)
        if not ok_write:
            raise RuntimeError("본문 작성 중 문제가 발생해 안전하게 중단했습니다.")

        orch.set_tags(req.tags)
        ok = orch.save_post()

        q.put({
            "type": "done", "ok": ok, "blog_id": blog_id,
            "msg": (f"임시저장 완료! https://blog.naver.com/{blog_id} → '내 글 관리 → 저장 글'에서 확인하세요."
                    if ok else "임시저장에 실패했어요. 로그를 확인해주세요(계정정보는 마스킹되어 기록됩니다)."),
        })
    except Exception as exc:
        logger.exception("publish 실패")
        q.put({"type": "done", "ok": False, "msg": f"오류가 발생했어요: {mask_secrets(str(exc))}"})
    finally:
        if orch is not None:
            try:
                orch.cleanup()
            except Exception:
                pass
        job["done"] = True


def _run_dry_run(req: PublishIn, emit, q: queue.Queue) -> None:
    """DRY_RUN=true: 네이버에 어떤 것도 실제로 입력/저장하지 않고 예정 동작만 보여준다."""
    emit("[DRY_RUN] 실제 네이버에는 아무 것도 입력/저장하지 않습니다.", 10)
    ordered = sorted(
        req.photos,
        key=lambda p: ({"작업 전": 0, "작업 중": 1, "작업 후": 2}.get(p.group.value if p.group else "", 9), p.order),
    )
    plan_lines = [f"제목: {req.title}", f"섹션 수: {len(req.sections)}", f"태그: {', '.join(req.tags)}",
                  f"사진 순서: " + " → ".join(f"[{p.group.value if p.group else '-'}]{p.filename}" for p in ordered)]
    for i, line in enumerate(plan_lines):
        emit(line, 20 + i * 15)
    q.put({
        "type": "done", "ok": True, "dry_run": True,
        "msg": "DRY_RUN 모드였습니다 — 실제 네이버 로그인/저장 없이 미리보기만 수행했습니다. "
               "실제로 저장하려면 .env의 DRY_RUN=false로 바꾸세요.",
        "plan": plan_lines,
    })
