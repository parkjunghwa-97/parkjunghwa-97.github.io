"""기프트클린 전용 글쓰기 엔진.

원본 저장소의 core/thread_expander.py 구조(Claude tool-use로 구조화 출력을 받는
방식)를 재사용하되, 프롬프트와 검증 규칙을 기프트클린 청소업체 블로그 기준으로
전면 교체했다.

이 모듈은 절대로:
- 입력되지 않은 현장 정보(작업 시간, 인력 수, 비용, 고객 반응 등)를 지어내지 않는다.
- 효과를 보장하거나 과장하는 표현을 쓰지 않는다.
- 금지 표현 목록에 있는 문구를 쓰지 않는다 (생성 후 검사 + 1회 재작성).
"""
from __future__ import annotations

import json
import logging
import re
from typing import Callable, Optional

from pydantic import BaseModel, Field

from config.settings import CLAUDE_MODEL, OPENAI_MODEL, MAX_OUTPUT_TOKENS
from models.giftclean_post import GiftCleanPostRequest, PostType, NATIONWIDE_SERVICES

logger = logging.getLogger(__name__)

COMPANY_NAME = "기프트클린"
BRAND_PHRASE = "깨끗한 공간, 새로운 시작을 선물합니다."

TITLE_MIN, TITLE_MAX = 20, 40
BODY_MIN_CHARS, BODY_MAX_CHARS = 2000, 3000

# 요청사항의 금지 표현 목록 — 생성 후 이 목록에 해당하는 문구가 있으면 경고하고 1회 재작성 시도한다.
FORBIDDEN_PHRASES = [
    "무조건 제거", "완벽 제거", "100% 복구", "최저가", "업계 1위",
    "무조건 보험 처리", "절대 재발하지 않음",
]

# 공통 안내 (요청사항 3단계 "공통 안내" 그대로) — 모델이 빠뜨리면 후처리로 보강한다.
COMMON_NOTICES = [
    "현장 상태와 오염도에 따라 작업 범위와 비용이 달라질 수 있습니다.",
    "추가 작업이 필요한 경우 사전에 안내한 뒤 진행합니다.",
    "사진만으로도 1차 상담이 가능합니다.",
]


class FaqItem(BaseModel):
    question: str
    answer: str


class PhotoCaption(BaseModel):
    group: str  # "작업 전" | "작업 중" | "작업 후"
    caption: str


class GeneratedGiftCleanPost(BaseModel):
    title: str
    sections: list[dict] = Field(default_factory=list)  # [{heading, body}]
    body: str = ""
    tags: list[str] = Field(default_factory=list)
    faq: list[FaqItem] = Field(default_factory=list)
    photo_captions: list[PhotoCaption] = Field(default_factory=list)
    char_count: int = 0
    warnings: list[str] = Field(default_factory=list)


# ── Claude tool-use 스키마 ──────────────────────────────────────────
WRITE_TOOL = {
    "name": "submit_giftclean_post",
    "description": "기프트클린 청소업체 블로그 글을 구조화하여 제출한다.",
    "input_schema": {
        "type": "object",
        "properties": {
            "title": {"type": "string", "description": "지역명+핵심 서비스 키워드 포함 제목, 20~40자"},
            "sections": {
                "type": "array",
                "description": "9단계 구조를 heading+body 쌍으로 표현 (필요한 단계만, 정보 없는 단계는 생략 가능)",
                "items": {
                    "type": "object",
                    "properties": {
                        "heading": {"type": "string"},
                        "body": {"type": "string"},
                    },
                    "required": ["heading", "body"],
                },
            },
            "tags": {"type": "array", "items": {"type": "string"}, "description": "3~5개"},
            "faq": {
                "type": "array",
                "description": "정확히 3개",
                "items": {
                    "type": "object",
                    "properties": {"question": {"type": "string"}, "answer": {"type": "string"}},
                    "required": ["question", "answer"],
                },
            },
            "photo_captions": {
                "type": "array",
                "description": "작업사례형일 때만: 각 사진 그룹(작업 전/작업 중/작업 후)별 짧은 설명 1~2개",
                "items": {
                    "type": "object",
                    "properties": {"group": {"type": "string"}, "caption": {"type": "string"}},
                    "required": ["group", "caption"],
                },
            },
        },
        "required": ["title", "sections", "tags", "faq"],
    },
}


def _service_area_note(req: GiftCleanPostRequest) -> str:
    if req.service_type in NATIONWIDE_SERVICES:
        return "이 서비스는 전국 출장 상담이 가능합니다."
    return "이 서비스는 수도권 중심으로 운영합니다."


def _facts_block(req: GiftCleanPostRequest) -> str:
    """사용자가 실제로 입력한 값만 나열한다 — 모델이 여기 없는 정보를 지어내지 못하게
    '입력된 사실'과 '입력되지 않은 항목'을 명확히 구분해서 보여준다."""
    lines = [
        f"- 글 유형: {req.post_type.value}",
        f"- 서비스 종류: {req.service_type.value}",
        f"- 주요 지역: {req.region}",
        f"- 핵심 주제: {req.topic}",
        f"- 현장/정보 메모: {req.memo}",
        f"- 핵심 키워드: {req.main_keyword}",
        f"- 보조 키워드: {', '.join(req.sub_keywords) if req.sub_keywords else '(없음)'}",
        f"- 문의 유도 문구(참고): {req.cta_phrase}",
    ]
    optional_fields = [
        ("평수", req.area_pyeong), ("작업 날짜", req.work_date),
        ("작업 전 상태", req.before_state), ("작업 과정", req.process_desc),
        ("작업 결과", req.result_desc), ("사용 장비/약품", req.equipment),
        ("고객 요청사항", req.customer_request), ("주의사항", req.precautions),
    ]
    for label, val in optional_fields:
        lines.append(f"- {label}: {val if val else '(입력되지 않음 — 지어내지 말 것)'}")
    return "\n".join(lines)


def _keyword_block(main_kw: str, sub_kws: list[str], question_kws: list[str]) -> str:
    parts = [f"메인 키워드: {main_kw}"]
    if sub_kws:
        parts.append(f"보조 키워드: {', '.join(sub_kws)}")
    if question_kws:
        parts.append(f"독자 질문형 키워드(FAQ에 반영): {', '.join(question_kws)}")
    return "\n".join(parts)


SYSTEM_PROMPT = f"""당신은 청소 전문업체 '{COMPANY_NAME}'의 블로그를 대신 쓰는 전문 작가입니다.
브랜드 문구: "{BRAND_PHRASE}"

## 절대 규칙 (위반 시 안 됨)
1. 과장하지 않는다. 확인되지 않은 효과를 단정하지 않는다. 청소 결과를 보장한다는 표현을 쓰지 않는다.
2. 공포를 과도하게 조장하지 않는다.
3. 실제 현장 경험과 전문적인 설명을 중심으로 쓰되, **입력되지 않은 사실(작업 시간, 인력 수,
   정확한 비용, 고객의 실제 반응/후기)은 절대로 지어내지 않는다.** 정보가 없으면 그 문장을
   생략하거나 "현장 상태에 따라 달라질 수 있습니다"라고 쓴다.
4. 광고 문구를 반복하지 않는다. 같은 키워드를 부자연스럽게 반복하지 않는다(스터핑 금지).
5. 의료·법률·보험 관련 내용은 확정적으로 단정하지 않는다.
6. 가격은 사용자가 실제로 입력했을 때만 구체적으로 적는다. 입력되지 않았으면 가격을 언급하지 않는다.
7. 다음 표현은 절대 쓰지 않는다: {', '.join(FORBIDDEN_PHRASES)}, 그리고 근거 없는 자격/수상/언론보도,
   입력되지 않은 고객 후기.
8. 작업 범위와 추가비 발생 조건은 "사전 안내 원칙"으로 쓴다 (예: 추가 작업이 필요하면 사전에
   안내 후 진행한다는 식).
9. 네이버 검색 노출을 보장한다는 표현을 쓰지 않는다.

## 글 구조 (9단계, 자연스럽게 소제목으로 구성)
1. 검색 의도를 반영한 제목
2. 고객 문제 또는 독자 질문
3. 핵심 답변 요약
4. 원인이나 판단 기준
5. 해결 방법 또는 작업 과정
6. 비용과 범위가 달라지는 요소
7. 주의사항
8. {COMPANY_NAME}의 작업 원칙
9. 상담 안내

## 제목 규칙
- 지역명과 핵심 서비스 키워드를 자연스럽게 포함, {TITLE_MIN}~{TITLE_MAX}자
- 클릭을 유도하되 자극적 표현은 피한다
- 동일 키워드를 반복하지 않는다, 사실과 다른 숫자/표현을 만들지 않는다

## 본문 규칙
- 한국어, 모바일 가독성 위해 문단을 짧게(2~3문장)
- 핵심 질문에 첫 부분에서 바로 답한다
- 전체 분량 {BODY_MIN_CHARS}~{BODY_MAX_CHARS}자(공백 포함) — 억지로 늘리지 않는다
- 아래 공통 안내를 자연스러운 위치에 포함한다:
  {chr(10).join('  - ' + n for n in COMMON_NOTICES)}

## SEO/AEO
- 제목, 도입부, 중간 소제목에 핵심 키워드를 자연스럽게 배치 (반복 횟수를 억지로 맞추지 않음)
- 독자가 검색할 가능성이 높은 질문 3~5개에 본문에서 직접 답한다
- 글 마지막에 FAQ 정확히 3개를 추가한다 (faq 필드)
- 지역명을 과도하게 나열하지 않는다

## 사진 설명 (작업사례형일 때만, photo_captions 필드)
- 작업 전 → 작업 중 → 작업 후 순서로 그룹별 짧은 설명 1~2개씩
- 사진 내용을 확실히 알 수 없으므로, 사용자가 입력한 memo/process_desc/result_desc 등의
  사실 정보에 근거해서만 설명을 쓰고, 사진 속 세부사항을 추측해서 단정하지 않는다

submit_giftclean_post 도구를 호출해 결과를 제출하세요.
"""


class GiftCleanWriter:
    """Claude(기본) 또는 GPT로 기프트클린 블로그 글 생성."""

    def __init__(self, provider: str = "claude", claude_api_key: Optional[str] = None,
                 openai_api_key: Optional[str] = None):
        self.provider = provider.lower()
        if self.provider == "claude" and claude_api_key:
            import anthropic
            self.client = anthropic.Anthropic(api_key=claude_api_key)
        elif self.provider == "openai" and openai_api_key:
            from openai import OpenAI
            self.client = OpenAI(api_key=openai_api_key)
        else:
            raise ValueError(
                f"'{provider}' 제공자의 API 키가 없습니다. .env에 CLAUDE_API_KEY 또는 "
                f"OPENAI_API_KEY를 설정하세요."
            )

    def generate(
        self,
        req: GiftCleanPostRequest,
        question_keywords: Optional[list[str]] = None,
        on_progress: Optional[Callable[[str], None]] = None,
    ) -> GeneratedGiftCleanPost:
        notify = on_progress or (lambda m: None)
        question_keywords = question_keywords or []

        user_prompt = (
            f"## 입력된 사실 정보\n{_facts_block(req)}\n\n"
            f"## 키워드\n{_keyword_block(req.main_keyword, req.sub_keywords, question_keywords)}\n\n"
            f"## 서비스 지역 범위 안내(그대로 반영)\n{_service_area_note(req)}\n\n"
            f"## 문의 유도 문구(마지막 상담 안내 단계에 자연스럽게 반영)\n{req.cta_phrase}\n"
        )
        if req.post_type == PostType.INFO:
            user_prompt += "\n이 글은 '정보형'입니다. 사진 설명(photo_captions)은 빈 배열로 두세요.\n"
        else:
            user_prompt += "\n이 글은 '작업사례형'입니다. photo_captions를 작업 전/중/후 순서로 채우세요.\n"

        notify("🤖 기프트클린 글을 작성하고 있어요...")
        data = self._invoke_with_retry(user_prompt, notify)
        result = self._build_result(data)
        notify(f"✅ 초안 완성: {result.title}")
        return result

    # ── 내부 ─────────────────────────────────────────────────

    def _invoke(self, user_prompt: str) -> dict:
        if self.provider == "claude":
            resp = self.client.messages.create(
                model=CLAUDE_MODEL,
                max_tokens=MAX_OUTPUT_TOKENS,
                system=SYSTEM_PROMPT,
                tools=[WRITE_TOOL],
                tool_choice={"type": "tool", "name": WRITE_TOOL["name"]},
                messages=[{"role": "user", "content": user_prompt}],
            )
            for block in resp.content:
                if getattr(block, "type", None) == "tool_use":
                    return dict(block.input)
            text = "".join(getattr(b, "text", "") for b in resp.content
                           if getattr(b, "type", None) == "text")
            return json.loads(self._extract_json(text))

        resp = self.client.chat.completions.create(
            model=OPENAI_MODEL,
            max_tokens=MAX_OUTPUT_TOKENS,
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT + "\n반드시 유효한 JSON으로만 응답하세요."},
                {"role": "user", "content": user_prompt},
            ],
        )
        return json.loads(self._extract_json(resp.choices[0].message.content))

    @staticmethod
    def _extract_json(text: str) -> str:
        text = (text or "").strip()
        if text.startswith("```"):
            text = text.split("\n", 1)[1] if "\n" in text else text
            if text.endswith("```"):
                text = text[:-3]
            text = text.strip()
        start, end = text.find("{"), text.rfind("}")
        if start != -1 and end != -1 and end > start:
            return text[start:end + 1]
        return text

    def _invoke_with_retry(self, user_prompt: str, notify: Callable, retries: int = 1) -> dict:
        """금지 표현이 남아있으면 1회만 피드백 재작성 (무한 재시도 금지, config/safety.MAX_STEP_RETRIES 취지)."""
        data = self._invoke(user_prompt)
        hits = self._forbidden_hits(data)
        if not hits or retries <= 0:
            return data
        notify(f"⚠️ 금지 표현 발견({', '.join(hits)}) — 다시 쓰는 중...")
        feedback = (
            user_prompt
            + f"\n\n## 재작성 지시\n직전 응답에 금지 표현이 포함되어 있었습니다: {', '.join(hits)}. "
              "이 표현들을 절대 쓰지 말고 다시 작성하세요."
        )
        data2 = self._invoke(feedback)
        return data2 if not self._forbidden_hits(data2) else data2  # 2차도 실패하면 경고만 남기고 진행

    @staticmethod
    def _forbidden_hits(data: dict) -> list[str]:
        text = json.dumps(data, ensure_ascii=False)
        return [p for p in FORBIDDEN_PHRASES if p in text]

    def _build_result(self, data: dict) -> GeneratedGiftCleanPost:
        sections = [s for s in (data.get("sections") or []) if isinstance(s, dict)]
        body = "\n\n".join(
            f"## {s.get('heading', '')}\n\n{s.get('body', '').strip()}" for s in sections
        ).strip()

        tags = []
        seen = set()
        for t in data.get("tags", []):
            t = str(t).strip().lstrip("#").strip()
            if t and t.lower() not in seen:
                tags.append(t)
                seen.add(t.lower())

        faq_raw = data.get("faq") or []
        faq = [FaqItem(question=str(f.get("question", "")), answer=str(f.get("answer", "")))
               for f in faq_raw if isinstance(f, dict)][:3]

        cap_raw = data.get("photo_captions") or []
        captions = [PhotoCaption(group=str(c.get("group", "")), caption=str(c.get("caption", "")))
                    for c in cap_raw if isinstance(c, dict)]

        title = str(data.get("title", "")).strip().strip('"').strip("'")
        char_count = len(re.sub(r"\s+", "", body))

        warnings: list[str] = []
        hits = self._forbidden_hits(data)
        if hits:
            warnings.append(f"금지 표현이 남아있습니다: {', '.join(hits)} — 발행 전 직접 수정하세요.")
        if len(title) < TITLE_MIN or len(title) > TITLE_MAX:
            warnings.append(f"제목이 {len(title)}자입니다 (권장 {TITLE_MIN}~{TITLE_MAX}자).")
        if char_count and (char_count < BODY_MIN_CHARS or char_count > BODY_MAX_CHARS * 1.2):
            warnings.append(f"본문이 {char_count}자입니다 (권장 {BODY_MIN_CHARS}~{BODY_MAX_CHARS}자).")
        if len(faq) < 3:
            warnings.append(f"FAQ가 {len(faq)}개입니다 (3개 권장).")

        return GeneratedGiftCleanPost(
            title=title, sections=sections, body=body, tags=tags[:5], faq=faq,
            photo_captions=captions, char_count=char_count, warnings=warnings,
        )
