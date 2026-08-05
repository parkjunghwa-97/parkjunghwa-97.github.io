"""로그·에러 메시지에서 계정정보·API 키를 마스킹하는 유틸리티.

요청사항: "실패한 단계와 원인을 로그에 남기되 계정정보와 API 키는 마스킹한다."
어떤 문자열이 로그로 나가기 전에 반드시 mask_secrets()를 통과시킨다.
"""
from __future__ import annotations

import os
import re


def _known_secret_values() -> list[str]:
    """.env에 실제로 설정된 비밀값들을 모아 마스킹 대상으로 삼는다."""
    names = [
        "NAVER_PW", "NAVER_ID",
        "ACCOUNT_1_PW", "ACCOUNT_2_PW", "ACCOUNT_1_ID", "ACCOUNT_2_ID",
        "CLAUDE_API_KEY", "OPENAI_API_KEY",
        "NAVER_CLIENT_ID", "NAVER_CLIENT_SECRET",
        "NAVER_SEARCHAD_API_KEY", "NAVER_SEARCHAD_SECRET_KEY", "NAVER_SEARCHAD_CUSTOMER_ID",
        "UNSPLASH_ACCESS_KEY",
    ]
    values = []
    for name in names:
        v = os.getenv(name)
        if v and len(v) >= 4:  # 너무 짧은 값(오탐 위험)은 마스킹 대상에서 제외
            values.append(v)
    return values


# 흔한 API 키 형태(긴 영숫자/하이픈 토큰)도 값 목록에 없더라도 보수적으로 가려준다.
_GENERIC_KEY_PATTERN = re.compile(r"\b(sk-[A-Za-z0-9_-]{10,}|[A-Za-z0-9_-]{24,})\b")


def mask_secrets(text: str) -> str:
    """문자열 안의 알려진 비밀값과 API-키형 토큰을 마스킹한다."""
    if not text:
        return text
    out = text
    for secret in _known_secret_values():
        if secret in out:
            visible = secret[:2]
            out = out.replace(secret, f"{visible}***MASKED***")
    out = _GENERIC_KEY_PATTERN.sub(lambda m: m.group(0)[:4] + "***MASKED***", out)
    return out


class SecretMaskingFilter:
    """logging.Filter 호환 필터 — 모든 로그 레코드의 메시지를 마스킹한다."""

    def filter(self, record) -> bool:  # noqa: A003 (logging.Filter 인터페이스 준수)
        try:
            record.msg = mask_secrets(str(record.msg))
            if record.args:
                record.args = tuple(
                    mask_secrets(a) if isinstance(a, str) else a for a in record.args
                )
        except Exception:
            pass
        return True
