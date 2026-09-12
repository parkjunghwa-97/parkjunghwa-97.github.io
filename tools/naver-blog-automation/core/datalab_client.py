"""네이버 데이터랩(검색어트렌드) API 클라이언트.

공식 엔드포인트: POST https://openapi.naver.com/v1/datalab/search
(개발자센터에서 발급받은 NAVER_DATALAB_CLIENT_ID/SECRET 필요 — 검색 API와 발급처는
같지만 별도 애플리케이션 등록이 필요할 수 있다).

주의(요청사항 그대로): 데이터랩 결과는 '상대 검색량 추세'이며 절대 검색량이 아니다.
이 클라이언트를 호출하는 쪽(core/keyword_research.py, UI)은 이 사실을 반드시 함께
표시해야 한다.
"""
from __future__ import annotations

import logging
from typing import Optional

import requests

logger = logging.getLogger(__name__)

DATALAB_URL = "https://openapi.naver.com/v1/datalab/search"


class NaverDataLabClient:
    def __init__(self, client_id: str, client_secret: str):
        self.client_id = client_id
        self.client_secret = client_secret

    def trend(self, keyword: str, start_date: str, end_date: str,
              time_unit: str = "month") -> Optional[list[dict]]:
        """지정 기간의 상대 검색 추세를 반환한다. 실패/미설정 시 None(호출부가 '확인 불가' 처리)."""
        if not self.client_id or not self.client_secret:
            return None
        headers = {
            "X-Naver-Client-Id": self.client_id,
            "X-Naver-Client-Secret": self.client_secret,
            "Content-Type": "application/json",
        }
        body = {
            "startDate": start_date,
            "endDate": end_date,
            "timeUnit": time_unit,
            "keywordGroups": [{"groupName": keyword, "keywords": [keyword]}],
        }
        try:
            resp = requests.post(DATALAB_URL, headers=headers, json=body, timeout=10)
            resp.raise_for_status()
            data = resp.json()
            results = data.get("results") or []
            if not results:
                return None
            return results[0].get("data", [])
        except requests.RequestException as exc:
            logger.warning(f"데이터랩 추세 조회 실패('{keyword}'): {exc}")
            return None

    @staticmethod
    def trend_direction(points: Optional[list[dict]]) -> str:
        """최근 구간이 초반 구간보다 높으면 '상승', 낮으면 '하락', 데이터 없으면 '확인 불가'."""
        if not points or len(points) < 2:
            return "확인 불가"
        values = [p.get("ratio", 0) for p in points]
        half = max(1, len(values) // 2)
        early = sum(values[:half]) / half
        recent = sum(values[half:]) / max(1, len(values) - half)
        if early == 0 and recent == 0:
            return "확인 불가"
        if recent > early * 1.1:
            return "상승"
        if recent < early * 0.9:
            return "하락"
        return "보합"
