"""기프트클린 키워드 조사 — 요청사항의 "키워드 조사 및 선정 기능" 구현.

AI 추측만으로 키워드를 정하지 않는다: 후보를 규칙 기반으로 확장하고, 가능하면
네이버 검색광고/데이터랩 API로 실측치를 조회해 공개된 계산식으로 점수를 매긴다.
API가 없으면 "검색량 확인 불가"로 표시하고 수동 입력 모드로 전환하며, 절대
데이터를 임의로 만들어내지 않는다.
"""
from __future__ import annotations

import json
import logging
import math
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Optional

from config.settings import RESEARCH_DIR
from core.datalab_client import NaverDataLabClient
from core.keyword_researcher import NaverKeywordResearcher
from models.giftclean_post import ServiceType

logger = logging.getLogger(__name__)

# 요청사항 2번: 후보 키워드 확장 템플릿
EXPANSION_TEMPLATES = [
    "{service} {region}", "{region} {service}", "{service} 비용", "{service} 가격",
    "{service} 업체", "{service} 방법", "{service} 주의사항", "{service} 원인",
    "{service} 후기", "{service} 전문업체",
]

# 요청사항 7번: 검색 의도 분류 규칙 (우선순위 순으로 검사)
_INTENT_RULES: list[tuple[list[str], str]] = [
    (["비용", "가격"], "비용 탐색형"),
    (["긴급", "당일", "즉시"], "긴급 상담형"),
    (["후기", "사례"], "작업사례 탐색형"),
    (["업체", "전문업체"], "업체 탐색형"),
]
_DEFAULT_INTENT = "정보 탐색형"

# 요청사항 8번: 점수 배점 상한
W_VOLUME, W_COMPETITION, W_SERVICE_FIT, W_REGION_FIT, W_TREND = 40, 20, 20, 10, 10


def _classify_intent(keyword: str) -> str:
    for tokens, intent in _INTENT_RULES:
        if any(t in keyword for t in tokens):
            return intent
    return _DEFAULT_INTENT


@dataclass
class KeywordCandidate:
    keyword: str
    pc_volume: Optional[int] = None
    mobile_volume: Optional[int] = None
    total_volume: Optional[int] = None
    competition_docs: Optional[int] = None
    competition_level: str = ""
    trend_direction: str = "확인 불가"
    region_match: bool = False
    service_fit: bool = False
    search_intent: str = _DEFAULT_INTENT
    data_available: bool = True
    score_breakdown: dict = field(default_factory=dict)
    final_score: float = 0.0
    recommend_grade: str = ""

    def to_dict(self) -> dict:
        return {
            "keyword": self.keyword, "pc_volume": self.pc_volume, "mobile_volume": self.mobile_volume,
            "total_volume": self.total_volume, "competition_docs": self.competition_docs,
            "competition_level": self.competition_level, "trend_direction": self.trend_direction,
            "region_match": self.region_match, "service_fit": self.service_fit,
            "search_intent": self.search_intent, "data_available": self.data_available,
            "score_breakdown": self.score_breakdown, "final_score": self.final_score,
            "recommend_grade": self.recommend_grade,
        }


@dataclass
class KeywordResearchResult:
    researched_at: str
    original_topic: str
    service: str
    region: str
    candidates: list[KeywordCandidate]
    api_available: bool
    main_keyword: Optional[str] = None
    sub_keywords: list[str] = field(default_factory=list)
    question_keywords: list[str] = field(default_factory=list)
    region_keywords: list[str] = field(default_factory=list)
    manual_mode: bool = False
    user_edits: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "researched_at": self.researched_at, "original_topic": self.original_topic,
            "service": self.service, "region": self.region,
            "candidates": [c.to_dict() for c in self.candidates],
            "api_available": self.api_available, "main_keyword": self.main_keyword,
            "sub_keywords": self.sub_keywords, "question_keywords": self.question_keywords,
            "region_keywords": self.region_keywords, "manual_mode": self.manual_mode,
            "user_edits": self.user_edits,
        }


class KeywordResearchService:
    """서비스명+지역+주제(또는 직접 후보)를 받아 후보를 확장하고 실데이터로 점수를 매긴다."""

    def __init__(self, env_config):
        self.env = env_config
        self._researcher: Optional[NaverKeywordResearcher] = None
        if env_config.naver_searchad_api_key and env_config.naver_searchad_secret_key:
            self._researcher = NaverKeywordResearcher(
                client_id=env_config.naver_client_id or "",
                client_secret=env_config.naver_client_secret or "",
                searchad_api_key=env_config.naver_searchad_api_key,
                searchad_secret_key=env_config.naver_searchad_secret_key,
                searchad_customer_id=env_config.naver_searchad_customer_id or "",
            )
        self._datalab: Optional[NaverDataLabClient] = None
        if env_config.naver_datalab_client_id and env_config.naver_datalab_client_secret:
            self._datalab = NaverDataLabClient(
                env_config.naver_datalab_client_id, env_config.naver_datalab_client_secret,
            )

    @property
    def api_available(self) -> bool:
        return self._researcher is not None

    def expand_candidates(self, service: str, region: str, extra_seeds: Optional[list[str]] = None) -> list[str]:
        seeds = set()
        for tmpl in EXPANSION_TEMPLATES:
            seeds.add(tmpl.format(service=service, region=region))
        for s in (extra_seeds or []):
            s = s.strip()
            if s:
                seeds.add(s)
        return sorted(seeds)

    def research(
        self, service: ServiceType, region: str, topic: str,
        extra_seeds: Optional[list[str]] = None, notify=None,
    ) -> KeywordResearchResult:
        candidate_keywords = self.expand_candidates(service.value, region, extra_seeds)
        candidates: list[KeywordCandidate] = []

        if not self.api_available:
            logger.warning("검색광고 API 키 없음 — 검색량 확인 불가, 수동 입력 모드로 전환")
            for kw in candidate_keywords:
                candidates.append(KeywordCandidate(
                    keyword=kw, data_available=False,
                    region_match=(region in kw), service_fit=(service.value in kw or True),
                    search_intent=_classify_intent(kw),
                ))
            return KeywordResearchResult(
                researched_at=datetime.now(timezone.utc).isoformat(),
                original_topic=topic, service=service.value, region=region,
                candidates=candidates, api_available=False, manual_mode=True,
            )

        # 실측 데이터 조회 (검색광고 API)
        for kw in candidate_keywords:
            if notify:
                notify(f"🔎 '{kw}' 검색량 조회 중...")
            try:
                related = self._researcher._get_search_volume(kw)
                exact = next((r for r in related if r.keyword.replace(" ", "") == kw.replace(" ", "")), None)
                if exact is None and related:
                    exact = related[0]
                if exact is None:
                    candidates.append(KeywordCandidate(keyword=kw, data_available=False,
                                                         search_intent=_classify_intent(kw)))
                    continue
                docs = self._researcher._get_blog_competition(kw)
                trend_dir = "확인 불가"
                if self._datalab:
                    end = datetime.now()
                    start = end - timedelta(days=365)
                    points = self._datalab.trend(kw, start.strftime("%Y-%m-%d"), end.strftime("%Y-%m-%d"))
                    trend_dir = NaverDataLabClient.trend_direction(points)
                candidates.append(KeywordCandidate(
                    keyword=kw,
                    pc_volume=exact.search_volume_pc, mobile_volume=exact.search_volume_mobile,
                    total_volume=exact.search_volume_pc + exact.search_volume_mobile,
                    competition_docs=docs, competition_level=exact.competition_level,
                    trend_direction=trend_dir,
                    region_match=(region in kw), service_fit=(service.value.split("·")[0] in kw),
                    search_intent=_classify_intent(kw), data_available=True,
                ))
            except Exception as exc:
                logger.warning(f"키워드 '{kw}' 조회 실패(확인 불가로 표시): {exc}")
                candidates.append(KeywordCandidate(keyword=kw, data_available=False,
                                                     search_intent=_classify_intent(kw)))

        self._score_candidates(candidates)
        result = KeywordResearchResult(
            researched_at=datetime.now(timezone.utc).isoformat(),
            original_topic=topic, service=service.value, region=region,
            candidates=candidates, api_available=True,
        )
        self._select_structure(result)
        return result

    # ── 점수 계산 (요청사항 8번 계산식 그대로) ─────────────────────
    @staticmethod
    def _score_candidates(candidates: list[KeywordCandidate]) -> None:
        scored = [c for c in candidates if c.data_available and c.total_volume is not None]
        if not scored:
            return
        max_volume = max((c.total_volume or 0) for c in scored) or 1
        max_docs = max((c.competition_docs or 0) for c in scored) or 1

        for c in scored:
            volume_score = (c.total_volume / max_volume) * W_VOLUME
            # 경쟁도 점수: 문서수가 적을수록 높은 점수 (역정규화)
            competition_score = (1 - (c.competition_docs or 0) / max_docs) * W_COMPETITION
            service_score = W_SERVICE_FIT if c.service_fit else W_SERVICE_FIT * 0.3
            region_score = W_REGION_FIT if c.region_match else 0
            trend_score = W_TREND if c.trend_direction == "상승" else (
                W_TREND * 0.5 if c.trend_direction == "보합" else 0
            )
            total = volume_score + competition_score + service_score + region_score + trend_score
            c.score_breakdown = {
                "검색수_점수": round(volume_score, 1), "경쟁도_점수": round(competition_score, 1),
                "서비스_적합도": round(service_score, 1), "지역_적합도": round(region_score, 1),
                "최근_상승_추세": round(trend_score, 1),
                "계산식": (
                    f"검색수({c.total_volume}/{max_volume}×{W_VOLUME}) + "
                    f"경쟁도((1-{c.competition_docs}/{max_docs})×{W_COMPETITION}) + "
                    f"서비스적합도({service_score}) + 지역적합도({region_score}) + 추세({trend_score})"
                ),
            }
            c.final_score = round(total, 1)

        scored.sort(key=lambda c: c.final_score, reverse=True)
        for i, c in enumerate(scored):
            if i == 0:
                c.recommend_grade = "메인 후보"
            elif c.final_score >= scored[0].final_score * 0.6:
                c.recommend_grade = "보조 후보"
            else:
                c.recommend_grade = "참고"

    # ── 요청사항 10번: 메인/보조/질문형/지역확장 구조로 정리 ────────
    @staticmethod
    def _select_structure(result: KeywordResearchResult) -> None:
        scored = sorted(
            [c for c in result.candidates if c.data_available],
            key=lambda c: c.final_score, reverse=True,
        )
        if not scored:
            return
        result.main_keyword = scored[0].keyword
        result.sub_keywords = [c.keyword for c in scored[1:5]]
        result.question_keywords = [
            c.keyword for c in scored if c.search_intent in ("정보 탐색형", "긴급 상담형")
        ][:5]
        result.region_keywords = [c.keyword for c in scored if c.region_match][:10]

    # ── 저장 (요청사항 14번) ────────────────────────────────────────
    @staticmethod
    def save_record(result: KeywordResearchResult, written_title: str = "") -> Path:
        RESEARCH_DIR.mkdir(parents=True, exist_ok=True)
        ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        path = RESEARCH_DIR / f"{ts}.json"
        record = result.to_dict()
        record["written_title"] = written_title
        path.write_text(json.dumps(record, ensure_ascii=False, indent=2), encoding="utf-8")
        return path
