"""7단계 테스트 1, 5: 글 생성 단위 테스트 / API 키 누락 테스트.

실제 Anthropic API를 호출하지 않고 client.messages.create를 목(mock)으로 대체한다.
"""
import pytest

from core.giftclean_writer import GiftCleanWriter, FORBIDDEN_PHRASES
from models.giftclean_post import GiftCleanPostRequest, PostType, ServiceType


class _FakeBlock:
    def __init__(self, data: dict):
        self.type = "tool_use"
        self.input = data


class _FakeResponse:
    def __init__(self, data: dict):
        self.content = [_FakeBlock(data)]


def _clean_data():
    return {
        "title": "서울 강동구 쓰레기집 청소 비용과 절차 총정리",
        "sections": [
            {"heading": "고객 문제", "body": "쓰레기집 청소를 고민하는 분들이 많습니다. " * 10},
            {"heading": "상담 안내", "body": "사진만으로도 1차 상담이 가능합니다. " * 10},
        ],
        "tags": ["쓰레기집청소", "강동구청소"],
        "faq": [
            {"question": "비용은 얼마인가요?", "answer": "현장 상태에 따라 달라질 수 있습니다."},
            {"question": "당일 작업이 가능한가요?", "answer": "사전 상담 후 일정 조율이 필요합니다."},
            {"question": "출장 상담이 가능한가요?", "answer": "전국 출장 상담이 가능합니다."},
        ],
        "photo_captions": [],
    }


def _forbidden_data():
    data = _clean_data()
    data["sections"][0]["body"] += " 완벽 제거를 보장합니다."
    return data


def test_missing_api_key_raises():
    with pytest.raises(ValueError):
        GiftCleanWriter(provider="claude", claude_api_key=None, openai_api_key=None)


def test_generate_builds_result_from_clean_response(monkeypatch):
    writer = GiftCleanWriter(provider="claude", claude_api_key="dummy-key-not-real")
    monkeypatch.setattr(writer.client.messages, "create", lambda **kw: _FakeResponse(_clean_data()))

    req = GiftCleanPostRequest(
        post_type=PostType.INFO, service_type=ServiceType.HOARDING, region="서울 강동구",
        topic="쓰레기집 청소 비용", memo="현장 메모", main_keyword="쓰레기집 청소",
        cta_phrase="사진만 보내주셔도 상담 가능합니다.",
    )
    result = writer.generate(req)
    assert "강동구" in result.title
    assert len(result.faq) == 3
    assert not any("금지 표현" in w for w in result.warnings)


def test_generate_retries_once_when_forbidden_phrase_present(monkeypatch):
    writer = GiftCleanWriter(provider="claude", claude_api_key="dummy-key-not-real")
    calls = {"n": 0}

    def fake_create(**kw):
        calls["n"] += 1
        return _FakeResponse(_forbidden_data() if calls["n"] == 1 else _clean_data())

    monkeypatch.setattr(writer.client.messages, "create", fake_create)

    req = GiftCleanPostRequest(
        post_type=PostType.INFO, service_type=ServiceType.HOARDING, region="서울 강동구",
        topic="쓰레기집 청소 비용", memo="현장 메모", main_keyword="쓰레기집 청소",
        cta_phrase="사진만 보내주셔도 상담 가능합니다.",
    )
    result = writer.generate(req)
    assert calls["n"] == 2  # 1차(금지표현) → 재작성 요청 → 2차(정상)
    assert "완벽 제거" not in result.body


def test_generate_warns_when_forbidden_phrase_survives_retry(monkeypatch):
    writer = GiftCleanWriter(provider="claude", claude_api_key="dummy-key-not-real")
    monkeypatch.setattr(writer.client.messages, "create", lambda **kw: _FakeResponse(_forbidden_data()))

    req = GiftCleanPostRequest(
        post_type=PostType.INFO, service_type=ServiceType.HOARDING, region="서울 강동구",
        topic="쓰레기집 청소 비용", memo="현장 메모", main_keyword="쓰레기집 청소",
        cta_phrase="사진만 보내주셔도 상담 가능합니다.",
    )
    result = writer.generate(req)
    assert any("금지 표현" in w for w in result.warnings)
    assert any(p in result.body for p in FORBIDDEN_PHRASES)
