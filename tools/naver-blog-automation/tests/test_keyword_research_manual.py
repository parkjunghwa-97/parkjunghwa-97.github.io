"""요청사항 12번: API가 없거나 실패하면 데이터를 임의로 만들지 않고 '확인 불가' + 수동 모드로 전환."""
from core.keyword_research import KeywordResearchService
from models.giftclean_post import ServiceType


class _NoApiEnv:
    naver_client_id = None
    naver_client_secret = None
    naver_searchad_api_key = None
    naver_searchad_secret_key = None
    naver_searchad_customer_id = None
    naver_datalab_client_id = None
    naver_datalab_client_secret = None


def test_manual_fallback_when_no_searchad_key():
    svc = KeywordResearchService(_NoApiEnv())
    assert svc.api_available is False

    result = svc.research(ServiceType.HOARDING, "서울 강동구", "쓰레기집 청소 비용")
    assert result.api_available is False
    assert result.manual_mode is True
    assert len(result.candidates) > 0
    for c in result.candidates:
        assert c.data_available is False
        assert c.total_volume is None  # 데이터를 임의로 만들어내지 않는다
        assert c.final_score == 0.0


def test_expand_candidates_uses_required_templates():
    svc = KeywordResearchService(_NoApiEnv())
    cands = svc.expand_candidates("쓰레기집 청소", "서울 강동구")
    assert "쓰레기집 청소 비용" in cands
    assert "쓰레기집 청소 가격" in cands
    assert "쓰레기집 청소 업체" in cands
    assert "쓰레기집 청소 후기" in cands
    assert "서울 강동구 쓰레기집 청소" in cands
    assert "쓰레기집 청소 서울 강동구" in cands


def test_search_intent_classification():
    from core.keyword_research import _classify_intent
    assert _classify_intent("쓰레기집 청소 비용") == "비용 탐색형"
    assert _classify_intent("쓰레기집 청소 업체") == "업체 탐색형"
    assert _classify_intent("쓰레기집 청소 후기") == "작업사례 탐색형"
    assert _classify_intent("쓰레기집 청소 긴급") == "긴급 상담형"
    assert _classify_intent("쓰레기집 청소 방법") == "정보 탐색형"
