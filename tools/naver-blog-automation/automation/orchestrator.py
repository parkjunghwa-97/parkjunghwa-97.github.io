"""기프트클린 포스팅 오케스트레이터.

원본 저장소의 automation/orchestrator.py 구조(단계별 실행 + 진행률 콜백)를
재사용하되, 기프트클린 입력 구조(사진 3그룹 + 캡션)에 맞게 인터리브 로직을
새로 작성했고, 안전장치(config/safety.py)를 여러 지점에 명시적으로 배선했다.

이 클래스는 절대로 발행(공개 게시) 버튼을 클릭하지 않는다 — editor.save()는
'발행' 계열 텍스트를 가진 버튼을 어떤 경로로도 클릭하지 않으며, 발행을
수행하는 함수 자체가 이 코드베이스에 존재하지 않는다.
"""
import logging
import time

from automation.browser import create_driver, close_driver
from automation.login import NaverLogin
from automation.editor import SmartEditorOne
from utils.env_loader import EnvConfig
from utils.clipboard import clipboard_clear
from utils.mask import mask_secrets

logger = logging.getLogger(__name__)


class PostingOrchestrator:
    """기프트클린 블로그 포스팅 워크플로우. 임시저장까지만 수행한다."""

    def __init__(self, env_config: EnvConfig, progress_callback=None,
                 human_pacing: bool | None = None, min_session_seconds: int | None = None):
        self.env = env_config
        self.driver = None
        self.editor: SmartEditorOne | None = None
        self._progress = progress_callback or (lambda s, p: None)
        self._cancelled = False
        self._session_start: float | None = None

        from config.settings import HUMAN_PACING_ENABLED, MIN_SESSION_SECONDS
        self.human_pacing = HUMAN_PACING_ENABLED if human_pacing is None else human_pacing
        self.min_session_seconds = (
            MIN_SESSION_SECONDS if min_session_seconds is None else min_session_seconds
        )

    def cancel(self):
        self._cancelled = True

    def _report(self, step: str, percent: int):
        safe_step = mask_secrets(step)
        self._progress(safe_step, percent)
        logger.info(f"[{percent}%] {safe_step}")

    # ── Phase 1: 브라우저 + 로그인 + 에디터 ──────────────────

    def open_and_login(self, blog_id: str, account: dict | None = None) -> bool:
        """브라우저 열기 → 로그인 → 에디터 진입.

        account가 없고 env.use_chrome_profile이 켜져 있으면 사용자 Chrome 프로필
        (기존 로그인 세션)을 재사용해 비밀번호 없이 진입을 시도한다 — 요청사항
        5단계 2번("가능하면 기존 로그인 세션이나 Chrome 프로필 재사용을 우선 검토").
        """
        self._report("브라우저 시작 중...", 5)
        use_profile = self.env.use_chrome_profile and not account
        self.driver = create_driver(
            use_profile=use_profile, profile_path=self.env.chrome_profile_path,
        )

        if self._cancelled:
            return False

        if use_profile:
            self._report("기존 Chrome 로그인 세션으로 에디터 진입 시도 중...", 15)
            self.driver.get(f"https://blog.naver.com/{blog_id}?Redirect=Write")
            time.sleep(2)
            if "nidlogin" not in self.driver.current_url:
                self._report("기존 세션으로 로그인 확인됨 (비밀번호 미사용)", 25)
                logged_in = True
            else:
                logger.info("기존 세션 로그인 실패 — 비밀번호 로그인으로 폴백")
                logged_in = False
        else:
            logged_in = False

        if not logged_in:
            naver_id = account["id"] if account else self.env.naver_id
            naver_pw = account["pw"] if account else self.env.naver_pw
            if not naver_id or not naver_pw:
                self._report("로그인 실패: 계정 정보 없음(.env 확인 필요)", 10)
                return False
            self._report("네이버 로그인 중...", 10)
            login_handler = NaverLogin(self.driver)
            if not login_handler.login(naver_id, naver_pw, blog_id=blog_id):
                self._report("로그인 실패!", 10)
                return False
            self._report("로그인 성공", 25)

        if self._cancelled:
            return False

        self._report("에디터 열고 있어요...", 30)
        self.editor = SmartEditorOne(self.driver)
        self.editor.navigate_to_editor(blog_id)
        self.editor.switch_to_mobile_view()

        self._session_start = time.monotonic()
        self._report("에디터 준비 완료!", 35)
        return True

    # ── Phase 2: 글 작성 (제목 + 섹션별 본문 + 사진 3그룹 + 캡션) ──

    def write_content(self, title: str, sections: list[dict], photo_plan: list[dict]) -> bool:
        """제목 → 섹션 본문 → (작업사례형이면) 작업 전/중/후 순서로 사진+캡션 삽입.

        photo_plan: [{"local_path": str, "group": "작업 전"|"작업 중"|"작업 후", "caption": str}, ...]
        이미 작업 전→중→후 순서로 정렬되어 들어온다고 가정한다(models.giftclean_post.photos_ordered).
        """
        if not self.editor:
            self._report("에디터가 준비되지 않았습니다", 0)
            return False
        if self._cancelled:
            return False

        self._report("제목을 입력하고 있어요...", 40)
        self.editor.input_title(title)
        self.editor.think_pause()

        total = max(len(sections), 1)
        for idx, sec in enumerate(sections):
            if self._cancelled:
                return False
            pct = 45 + int((idx / total) * 25)
            self._report(f"본문을 작성 중... ({idx + 1}/{total})", pct)
            heading = sec.get("heading", "")
            body = sec.get("body", "").strip()
            text = f"## {heading}\n\n{body}" if heading else body
            if idx == 0:
                self.editor.input_body(text)
            else:
                self.editor.input_body_chunk(text)
            self.editor.reread_scroll()
            self.editor.think_pause()

        n_photos = len(photo_plan)
        for i, item in enumerate(photo_plan):
            if self._cancelled:
                return False
            pct = 70 + int((i / max(n_photos, 1)) * 12)
            self._report(f"사진 삽입 중... ({i + 1}/{n_photos}, {item.get('group', '')})", pct)
            ok = self.editor.upload_images([item["local_path"]])
            if ok and item.get("caption"):
                self.editor.set_last_image_caption(item["caption"])
            self.editor.think_pause()

        self._report("글+사진 작성 완료", 83)
        return True

    # ── Phase 2-5: 태그 설정 (카테고리는 이 도구 범위에 없음) ────

    def set_tags(self, tags: list[str]) -> bool:
        if not self.editor or not tags:
            return True
        if self._cancelled:
            return False
        self._report("태그 입력창을 여는 중...", 86)
        opened = self.editor.open_settings_panel()
        if not opened:
            logger.info("설정 패널 없이 인라인 태그 입력 시도")
        self._report(f"태그 설정 중: {', '.join(tags[:3])}", 88)
        self.editor.set_tags(tags)
        return True

    # ── Phase 3: 저장 (임시저장 전용) ────────────────────────

    def save_post(self) -> bool:
        """임시저장(발행 아님). editor.save()는 '발행' 계열 텍스트를 가진 버튼을
        어떤 경로로도 클릭하지 않는다 — config.safety.FORBIDDEN_BUTTON_TEXTS 참고.
        이 프로젝트에는 발행을 수행하는 함수 자체가 존재하지 않는다."""
        if not self.editor:
            self._report("에디터가 준비되지 않았습니다", 0)
            return False
        if self._cancelled:
            return False

        if self.human_pacing:
            self.ensure_min_session_time()

        self._report("임시저장 중...", 92)
        success = self.editor.save()

        if success:
            self._report("임시저장 완료!", 100)
        else:
            self._report("임시저장 실패 — 로그를 확인하세요 (안전하게 중단됨)", 95)
        return success

    def ensure_min_session_time(self) -> None:
        if self._session_start is None or self.min_session_seconds <= 0:
            return
        elapsed = time.monotonic() - self._session_start
        remaining = self.min_session_seconds - elapsed
        if remaining <= 0:
            logger.info(f"체류시간 충분({elapsed:.0f}s) — 바로 저장")
            return
        self._report(f"검토 중... (+{remaining:.0f}초)", 90)
        end = time.monotonic() + remaining
        import random
        while time.monotonic() < end:
            if self._cancelled:
                return
            if self.editor:
                self.editor.reread_scroll(probability=0.7)
            nap = min(random.uniform(4, 9), max(0.5, end - time.monotonic()))
            time.sleep(nap)

    # ── 정리 ─────────────────────────────────────────────────

    def cleanup(self):
        clipboard_clear()
        if self.driver:
            close_driver(self.driver)
            self.driver = None
            self.editor = None

    @property
    def is_browser_alive(self) -> bool:
        if not self.driver:
            return False
        try:
            _ = self.driver.current_url
            return True
        except Exception:
            return False
