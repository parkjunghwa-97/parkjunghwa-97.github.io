from __future__ import annotations

import hashlib
import hmac
import base64
import time
import logging

import requests

from models.keyword import KeywordResult
from utils.retry import retry

logger = logging.getLogger(__name__)


class NaverKeywordResearcher:
    """네이버 Search API + SearchAd API 키워드 리서치."""

    def __init__(
        self,
        client_id: str,
        client_secret: str,
        searchad_api_key: str,
        searchad_secret_key: str,
        searchad_customer_id: str,
    ):
        self.client_id = client_id
        self.client_secret = client_secret
        self.searchad_api_key = searchad_api_key
        self.searchad_secret_key = searchad_secret_key
        self.searchad_customer_id = searchad_customer_id

    def research(self, seed_keyword: str, max_count: int = 20, on_progress=None) -> list:
        """
        키워드 리서치 전체 플로우:
        1. SearchAd API → 연관 키워드 + 검색량
        2. 검색량 상위 max_count개만 선별
        3. Blog Search API → 경쟁도 (블로그 포스트 수)
        4. 골든 스코어 계산 + 정렬

        on_progress: callable(current, total, phase) — 진행 상황 콜백
        """
        if on_progress:
            on_progress(0, 1, "연관 키워드 조회 중...")

        related = self._get_search_volume(seed_keyword)

        # 검색량(PC+Mobile) 상위 max_count개만 남겨서 경쟁도 조회 시간 절약
        related.sort(key=lambda x: x.search_volume_pc + x.search_volume_mobile, reverse=True)
        related = related[:max_count]
        total = len(related)

        for i, kw in enumerate(related):
            if on_progress:
                on_progress(i, total, f"경쟁도 분석 중... ({i+1}/{total})")
            kw.competition = self._get_blog_competition(kw.keyword)
            kw.calculate_golden_score()
            time.sleep(0.1)

        if on_progress:
            on_progress(total, total, "정렬 중...")

        # 원시 비율을 0~100 점수로 정규화
        max_ratio = max((kw._raw_ratio for kw in related), default=1) or 1
        for kw in related:
            kw.golden_score = round(kw._raw_ratio / max_ratio * 100, 1)

        related.sort(key=lambda x: x.golden_score, reverse=True)
        logger.info(f"Keyword research complete: {len(related)} keywords for '{seed_keyword}'")
        return related

    def _generate_signature(self, timestamp: str, method: str, uri: str) -> str:
        """SearchAd API용 HMAC-SHA256 서명 생성."""
        message = f"{timestamp}.{method}.{uri}"
        sign = hmac.new(
            self.searchad_secret_key.encode("utf-8"),
            message.encode("utf-8"),
            hashlib.sha256,
        )
        return base64.b64encode(sign.digest()).decode("utf-8")

    @retry(max_attempts=3, exceptions=(requests.RequestException,))
    def _get_search_volume(self, keyword: str) -> list:
        """SearchAd keywordstool API → 검색량 + 연관 키워드."""
        uri = "/keywordstool"
        method = "GET"
        timestamp = str(int(time.time() * 1000))
        signature = self._generate_signature(timestamp, method, uri)

        headers = {
            "X-API-KEY": self.searchad_api_key,
            "X-Customer": self.searchad_customer_id,
            "X-Timestamp": timestamp,
            "X-Signature": signature,
        }
        # SearchAd API는 공백이 포함된 키워드를 거부(400)함
        # 공백을 제거하여 복합 키워드로 전달 (쉼표 분리 시 별개 키워드로 취급되어 무관한 결과 포함됨)
        hint = keyword.replace(" ", "")
        params = {
            "hintKeywords": hint,
            "showDetail": "1",
        }

        resp = requests.get(
            f"https://api.searchad.naver.com{uri}",
            headers=headers,
            params=params,
            timeout=10,
        )
        resp.raise_for_status()
        data = resp.json()

        results = []
        for item in data.get("keywordList", []):
            pc_vol = item.get("monthlyPcQcCnt", 0)
            mobile_vol = item.get("monthlyMobileQcCnt", 0)
            # "< 10" 문자열 처리
            if isinstance(pc_vol, str):
                pc_vol = 5
            if isinstance(mobile_vol, str):
                mobile_vol = 5

            results.append(KeywordResult(
                keyword=item.get("relKeyword", ""),
                search_volume_pc=int(pc_vol),
                search_volume_mobile=int(mobile_vol),
                competition_level=item.get("compIdx", ""),
            ))

        logger.info(f"SearchAd returned {len(results)} keywords for '{keyword}'")
        return results

    def _get_blog_competition(self, keyword: str) -> int:
        """Blog Search API → 블로그 포스트 수 (경쟁 지표)."""
        headers = {
            "X-Naver-Client-Id": self.client_id,
            "X-Naver-Client-Secret": self.client_secret,
        }
        params = {"query": keyword, "display": 1, "start": 1}

        try:
            resp = requests.get(
                "https://openapi.naver.com/v1/search/blog",
                headers=headers,
                params=params,
                timeout=10,
            )
            resp.raise_for_status()
            total = resp.json().get("total", 0)
            logger.debug(f"Blog competition for '{keyword}': {total}")
            return total
        except requests.RequestException as e:
            logger.warning(f"Blog competition lookup failed for '{keyword}': {e}")
            return 0
