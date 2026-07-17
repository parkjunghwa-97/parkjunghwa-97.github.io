from __future__ import annotations

from dataclasses import dataclass


@dataclass
class KeywordResult:
    """키워드 리서치 결과."""
    keyword: str
    search_volume_pc: int = 0
    search_volume_mobile: int = 0
    total_search_volume: int = 0
    competition: int = 0
    competition_level: str = ""
    golden_score: float = 0.0

    def calculate_golden_score(self) -> None:
        self.total_search_volume = self.search_volume_pc + self.search_volume_mobile
        # 원시 비율 저장 (나중에 정규화에 사용)
        self._raw_ratio = self.total_search_volume / (self.competition + 1)
