"""안전장치 중앙 관리 모듈.

이 파일이 이 프로젝트의 유일한 "발행 허용 여부" 진실 공급원(source of truth)이다.
다른 모듈은 이 파일의 상수/함수만 참조해야 하며, 자체적으로 발행 여부를 판단하지 않는다.

요청 사항(6단계 안전장치) 반영:
- 자동 발행 금지 플래그 (ALLOW_PUBLISH)
- 코드 내부에서도 발행 관련 함수 호출을 차단
- localhost 외부 접속 차단
- 업로드 파일 확장자/크기 검사
- 1회 실행당 최대 글 1개
- 대량 반복 실행 / 예약 실행 기능 비활성화
- 자동 댓글·공감·이웃추가 기능 금지
- CAPTCHA 우회·탐지 회피 기능을 새로 추가하지 않음 (이 파일은 그런 기능을 제공하지 않는다)
"""
from __future__ import annotations

import os
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent


def _bool_env(name: str, default: bool) -> bool:
    val = os.getenv(name)
    if val is None:
        return default
    return val.strip().lower() in ("1", "true", "yes", "on")


# ── 발행 금지 (가장 중요) ────────────────────────────────────────────
# ALLOW_PUBLISH는 항상 False로 강제한다. .env에 이 값을 true로 넣어도
# 이 모듈은 이를 무시하고 False를 반환한다 — "발행 기능 자체가 없다"는
# 요구사항을 코드로 강제하기 위함이다. 향후 실제 발행 기능이 필요해지면
# 이 모듈을 사람이 직접, 의도적으로 수정해야만 한다(설정값 하나로 못 바뀜).
ALLOW_PUBLISH: bool = False


def assert_publish_forbidden() -> None:
    """발행 관련 동작을 시도하기 전에 반드시 호출한다.

    이 프로젝트에는 '발행'을 수행하는 함수가 존재하지 않는다. 이 함수는
    누군가 실수로(혹은 향후 변경으로) 발행 경로를 추가하려 할 때 즉시
    예외를 던져 막기 위한 방어선이다.
    """
    if not ALLOW_PUBLISH:
        raise RuntimeError(
            "발행(공개 게시)은 이 프로그램에서 지원하지 않습니다. "
            "ALLOW_PUBLISH는 코드에서 항상 False로 고정되어 있습니다. "
            "임시저장만 지원합니다."
        )


# 네이버 에디터에서 '절대' 클릭하면 안 되는 버튼 텍스트 목록.
# automation/editor.py의 모든 클릭 후보 탐색은 이 목록에 포함된 텍스트를
# 가진 요소를 최종 후보에서 제외해야 한다.
FORBIDDEN_BUTTON_TEXTS: tuple[str, ...] = (
    "발행", "예약발행", "예약 발행", "공개발행", "전체공개", "공개 설정",
    "즉시발행", "발행하기", "Publish",
)


# ── DRY_RUN ──────────────────────────────────────────────────────────
# true면 네이버에 어떤 것도 실제로 입력/저장하지 않고, 생성된 글/사진 배치/
# 태그/예정 동작만 화면에 보여준다. 최초 설치 시 안전을 위해 기본값 true.
DRY_RUN: bool = _bool_env("DRY_RUN", True)


# ── localhost 외부 접속 차단 ─────────────────────────────────────────
# 이 서버는 항상 127.0.0.1에서만 bind한다. 0.0.0.0 등 외부 인터페이스로
# 여는 것은 이 프로젝트의 위협 모델(로컬 단일 사용자)을 벗어나므로 막는다.
SERVER_HOST: str = "127.0.0.1"
SERVER_PORT: int = int(os.getenv("PORT", "8787"))


def enforce_local_host(requested_host: str) -> str:
    """서버 bind host를 강제로 로컬 전용으로 고정한다."""
    if requested_host not in ("127.0.0.1", "localhost"):
        raise RuntimeError(
            f"이 앱은 localhost에서만 실행할 수 있습니다 (요청된 host: {requested_host!r}). "
            "외부에 노출하지 마세요."
        )
    return requested_host


# ── 업로드 검증 ──────────────────────────────────────────────────────
ALLOWED_IMAGE_EXTENSIONS: tuple[str, ...] = (".jpg", ".jpeg", ".png", ".webp", ".gif")
MAX_IMAGE_SIZE_MB: int = int(os.getenv("MAX_IMAGE_SIZE_MB", "20"))
MAX_IMAGES_PER_POST: int = int(os.getenv("MAX_IMAGES_PER_POST", "60"))


def validate_image_extension(filename: str) -> bool:
    return Path(filename).suffix.lower() in ALLOWED_IMAGE_EXTENSIONS


def validate_image_size(size_bytes: int) -> bool:
    return size_bytes <= MAX_IMAGE_SIZE_MB * 1024 * 1024


# ── 1회 실행당 최대 글 1개 / 대량·예약 실행 차단 ─────────────────────
# 이 값들은 상수이며 .env로 바꿀 수 없다 — "설정으로 우회 가능한 안전장치"는
# 안전장치가 아니라는 원칙에 따름.
MAX_POSTS_PER_RUN: int = 1
BULK_MODE_ENABLED: bool = False       # 여러 글 순차/반복 발행 기능 없음
SCHEDULED_MODE_ENABLED: bool = False  # 예약 실행(cron 등) 기능 없음

# ── 금지 부가 기능 ───────────────────────────────────────────────────
# 아래 기능들은 이 프로젝트에 구현되어 있지 않으며, 앞으로도 추가하지 않는다.
AUTO_COMMENT_ENABLED: bool = False
AUTO_LIKE_ENABLED: bool = False
AUTO_NEIGHBOR_ADD_ENABLED: bool = False
CAPTCHA_BYPASS_ENABLED: bool = False
DETECTION_EVASION_FEATURES_ENABLED: bool = False


def enforce_single_post_run(requested_count: int) -> None:
    if requested_count > MAX_POSTS_PER_RUN:
        raise RuntimeError(
            f"1회 실행당 최대 {MAX_POSTS_PER_RUN}개 글만 작성할 수 있습니다 "
            f"(요청: {requested_count}개). 대량/반복 발행은 지원하지 않습니다."
        )


# ── 재시도 상한 (무한 재시도 금지) ───────────────────────────────────
MAX_STEP_RETRIES: int = 2
