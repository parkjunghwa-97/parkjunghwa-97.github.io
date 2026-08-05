from __future__ import annotations

import os
import warnings
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv

REQUIRED_VARS = ["NAVER_ID", "NAVER_PW", "BLOG_ID"]


class EnvConfig:
    """.env 설정 로드 및 검증.

    주의: 계정 정보를 평문(.env)으로 저장하는 것은 위험을 수반한다.
    가능하면 naver_chrome_profile_reuse를 사용해 비밀번호 없이 기존 로그인
    세션을 재사용하는 방식을 우선 시도하라 (automation/browser.py 참고).
    """

    def __init__(self, env_path: str = None):
        if env_path is None:
            env_path = Path(__file__).parent.parent / ".env"
        load_dotenv(env_path)
        self._validate()

    def _validate(self):
        has_account = all(os.getenv(v) for v in REQUIRED_VARS)
        has_profile_reuse = self.use_chrome_profile
        if not has_account and not has_profile_reuse:
            raise EnvironmentError(
                "계정 정보가 없습니다. .env에 NAVER_ID/NAVER_PW/BLOG_ID를 설정하거나, "
                "USE_CHROME_PROFILE=true로 기존 로그인 세션 재사용을 설정하세요."
            )
        if not os.getenv("CLAUDE_API_KEY") and not os.getenv("OPENAI_API_KEY"):
            warnings.warn("LLM API 키가 없습니다. 글 생성 기능을 사용할 수 없습니다.")
        if not os.getenv("NAVER_SEARCHAD_API_KEY") or not os.getenv("NAVER_SEARCHAD_SECRET_KEY"):
            warnings.warn("네이버 검색광고 API 키가 없습니다. 키워드 검색량 조회가 '확인 불가'로 표시됩니다.")

    # ── 계정 ──────────────────────────────────────────────────
    @property
    def naver_id(self) -> Optional[str]:
        return os.getenv("NAVER_ID")

    @property
    def naver_pw(self) -> Optional[str]:
        return os.getenv("NAVER_PW")

    @property
    def blog_id(self) -> Optional[str]:
        return os.getenv("BLOG_ID")

    @property
    def use_chrome_profile(self) -> bool:
        """true면 비밀번호 로그인 대신 사용자 Chrome 프로필(기존 로그인 세션) 재사용을 우선 시도."""
        return (os.getenv("USE_CHROME_PROFILE", "false") or "").strip().lower() in ("1", "true", "yes")

    @property
    def chrome_profile_path(self) -> Optional[str]:
        return os.getenv("CHROME_PROFILE_PATH") or None

    # ── LLM ───────────────────────────────────────────────────
    @property
    def claude_api_key(self) -> Optional[str]:
        return os.getenv("CLAUDE_API_KEY")

    @property
    def openai_api_key(self) -> Optional[str]:
        return os.getenv("OPENAI_API_KEY")

    # ── 네이버 검색/검색광고 API (키워드 조사) ───────────────────
    @property
    def naver_client_id(self) -> Optional[str]:
        return os.getenv("NAVER_CLIENT_ID")

    @property
    def naver_client_secret(self) -> Optional[str]:
        return os.getenv("NAVER_CLIENT_SECRET")

    @property
    def naver_searchad_api_key(self) -> Optional[str]:
        return os.getenv("NAVER_SEARCHAD_API_KEY")

    @property
    def naver_searchad_secret_key(self) -> Optional[str]:
        return os.getenv("NAVER_SEARCHAD_SECRET_KEY")

    @property
    def naver_searchad_customer_id(self) -> Optional[str]:
        return os.getenv("NAVER_SEARCHAD_CUSTOMER_ID")

    @property
    def naver_datalab_client_id(self) -> Optional[str]:
        return os.getenv("NAVER_DATALAB_CLIENT_ID")

    @property
    def naver_datalab_client_secret(self) -> Optional[str]:
        return os.getenv("NAVER_DATALAB_CLIENT_SECRET")

    # ── 회사 연락처 기본값 (문의 유도 문구에 사용, 입력값이 없을 때만) ──
    @property
    def giftclean_kakao_channel(self) -> Optional[str]:
        return os.getenv("GIFTCLEAN_KAKAO_CHANNEL")

    @property
    def giftclean_phone(self) -> Optional[str]:
        return os.getenv("GIFTCLEAN_PHONE")

    @property
    def giftclean_homepage(self) -> Optional[str]:
        return os.getenv("GIFTCLEAN_HOMEPAGE")
