import os
from pathlib import Path

# Paths
PROJECT_ROOT = Path(__file__).parent.parent
LOG_DIR = PROJECT_ROOT / "logs"
ASSETS_DIR = PROJECT_ROOT / "assets"
RESEARCH_DIR = PROJECT_ROOT / "eval" / "keyword_research"
CHROME_PROFILE_DIR = PROJECT_ROOT / ".chrome_profile"  # 로그인 세션 재사용용 (요청 5단계 2번)

# URLs
NAVER_LOGIN_URL = "https://nid.naver.com/nidlogin.login"
NAVER_BLOG_WRITE_URL = "https://blog.naver.com/{blog_id}?Redirect=Write"

# Timeouts (seconds)
PAGE_LOAD_TIMEOUT = 30
ELEMENT_WAIT_TIMEOUT = 15
LOGIN_WAIT_TIMEOUT = 10
EDITOR_LOAD_TIMEOUT = 20
CLIPBOARD_PASTE_DELAY = 0.5
TYPING_DELAY = 0.03

# Retry — 무한 재시도 금지 (config/safety.py의 MAX_STEP_RETRIES와 별개로,
# 개별 UI 조작 단계는 여기 정의된 낮은 상한만 사용한다)
MAX_RETRIES = 2
RETRY_BACKOFF_BASE = 2

# LLM
DEFAULT_LLM_PROVIDER = "claude"
CLAUDE_MODEL = "claude-sonnet-4-6"
OPENAI_MODEL = "gpt-4o"
MAX_TOKENS = 8192
MAX_OUTPUT_TOKENS = 16000

# Image
SUPPORTED_IMAGE_FORMATS = [".jpg", ".jpeg", ".png", ".gif", ".webp"]

# Human pacing (네이버 저품질 회피 — 사람처럼 작성하는 체류시간 시뮬레이션).
# 이는 '탐지 회피'가 아니라 실제 사람이 검토하며 쓰는 것과 같은 자연스러운
# 체류시간을 두는 것으로, 요청사항의 "탐지 회피 기능 신규 추가 금지"와는
# 별개로 원본 저장소에 이미 있던 동작을 그대로 유지한다(신규 추가 아님).
HUMAN_PACING_ENABLED = True
MIN_SESSION_SECONDS = int(os.getenv("MIN_SESSION_SECONDS", "180"))
THINK_PAUSE_RANGE = (2.0, 6.0)
REREAD_PROBABILITY = 0.3
