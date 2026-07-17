"""7단계 테스트 4, 5, 9: 입력값 누락 / API 키 누락 / 발행 함수 차단(업로드·확인 게이트).

FastAPI TestClient로 서버를 직접 호출한다 (.env는 tests/conftest.py가 아니라
이 파일이 os.environ으로 임시 세팅한다 — 실제 .env 파일을 건드리지 않는다).
"""
import base64
import os

import pytest
from fastapi.testclient import TestClient


@pytest.fixture()
def client(monkeypatch, tmp_path):
    monkeypatch.setenv("NAVER_ID", "test_id")
    monkeypatch.setenv("NAVER_PW", "test_pw")
    monkeypatch.setenv("BLOG_ID", "test_blog")
    monkeypatch.setenv("DRY_RUN", "true")
    monkeypatch.delenv("CLAUDE_API_KEY", raising=False)
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.delenv("NAVER_SEARCHAD_API_KEY", raising=False)

    import importlib
    import web.server as server_module
    importlib.reload(server_module)  # 새 환경변수로 EnvConfig 다시 로드
    return TestClient(server_module.app)


def test_status_reports_dry_run_and_no_publish(client):
    r = client.get("/api/status")
    assert r.status_code == 200
    body = r.json()
    assert body["dry_run"] is True
    assert body["allow_publish"] is False


def test_generate_missing_api_key_returns_400(client):
    payload = {
        "post": {
            "post_type": "정보형", "service_type": "쓰레기집 청소", "region": "서울",
            "topic": "t", "memo": "m", "main_keyword": "k", "cta_phrase": "c",
        },
        "keywords": {},
    }
    r = client.post("/api/generate", json=payload)
    assert r.status_code == 400
    assert "API_KEY" in r.json()["detail"]


def test_generate_missing_required_field_returns_422(client):
    payload = {"post": {"post_type": "정보형", "service_type": "쓰레기집 청소"}, "keywords": {}}
    r = client.post("/api/generate", json=payload)
    assert r.status_code == 422  # pydantic 필수값 검증


def test_generate_case_post_without_photos_returns_400_business_rule(client):
    payload = {
        "post": {
            "post_type": "작업사례형", "service_type": "화재청소", "region": "서울",
            "topic": "t", "memo": "m", "main_keyword": "k", "cta_phrase": "c", "photos": [],
        },
        "keywords": {},
    }
    r = client.post("/api/generate", json=payload)
    assert r.status_code == 400
    assert "사진" in r.json()["detail"]


def test_publish_without_confirmation_is_rejected(client):
    payload = {"title": "t", "sections": [{"heading": "h", "body": "b"}], "tags": [], "photos": [], "confirmed": False}
    r = client.post("/api/publish", json=payload)
    assert r.status_code == 400


def test_publish_rejects_disallowed_extension(client):
    payload = {
        "title": "t", "sections": [{"heading": "h", "body": "b"}], "tags": [],
        "photos": [{"media_type": "application/x-msdownload", "data": "AAAA",
                     "filename": "virus.exe", "order": 0, "caption": "", "strip_gps": True}],
        "confirmed": True,
    }
    r = client.post("/api/publish", json=payload)
    assert r.status_code == 400
    assert "확장자" in r.json()["detail"]


def test_publish_rejects_oversized_image(client):
    big = base64.b64encode(b"0" * (21 * 1024 * 1024)).decode()  # 21MB > 기본 20MB 제한
    payload = {
        "title": "t", "sections": [{"heading": "h", "body": "b"}], "tags": [],
        "photos": [{"media_type": "image/jpeg", "data": big, "filename": "a.jpg",
                     "order": 0, "caption": "", "strip_gps": True}],
        "confirmed": True,
    }
    r = client.post("/api/publish", json=payload)
    assert r.status_code == 400
    assert "용량" in r.json()["detail"]


def test_publish_accepts_valid_dry_run_request(client):
    onepx = base64.b64encode(bytes.fromhex(
        "89504e470d0a1a0a0000000d4948445200000001000000010802000000907724"
        "b60000000c4944415478da6364f8cf000000010001aa16687b0000000049454e"
        "44ae426082"
    )).decode()
    payload = {
        "title": "제목", "sections": [{"heading": "h", "body": "b"}], "tags": ["a"],
        "photos": [{"media_type": "image/png", "data": onepx, "filename": "a.png",
                     "group": "작업 전", "order": 0, "caption": "설명", "strip_gps": True}],
        "confirmed": True,
    }
    r = client.post("/api/publish", json=payload)
    assert r.status_code == 200
    body = r.json()
    assert body["dry_run"] is True
    assert "job_id" in body
