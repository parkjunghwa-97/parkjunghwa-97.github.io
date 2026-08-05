"""7단계 테스트 6, 7, 8, 9: 로그인 실패 / 셀렉터 실패 / 임시저장 직전 중단 / 발행 함수 차단.

실제 Chrome/Selenium 없이 automation.orchestrator.create_driver, NaverLogin,
SmartEditorOne을 모두 monkeypatch로 대체해 오케스트레이션 '로직'만 검증한다.
(conftest.py가 selenium/undetected_chromedriver를 임포트 가능한 가짜 모듈로 대체해둔다)
"""
from unittest.mock import MagicMock

import pytest
from selenium.common.exceptions import TimeoutException  # conftest가 등록한 가짜 모듈

from automation.orchestrator import PostingOrchestrator


class _FakeEnv:
    naver_id = "test_id"
    naver_pw = "test_pw"
    blog_id = "test_blog"
    use_chrome_profile = False
    chrome_profile_path = None


def _patched_orchestrator(monkeypatch, login_result: bool):
    fake_driver = MagicMock()
    monkeypatch.setattr("automation.orchestrator.create_driver", lambda **kw: fake_driver)
    monkeypatch.setattr("automation.orchestrator.close_driver", lambda d: None)

    fake_login = MagicMock()
    fake_login.login.return_value = login_result
    monkeypatch.setattr("automation.orchestrator.NaverLogin", lambda driver: fake_login)

    fake_editor = MagicMock()
    fake_editor.navigate_to_editor.return_value = None
    fake_editor.switch_to_mobile_view.return_value = True
    monkeypatch.setattr("automation.orchestrator.SmartEditorOne", lambda driver: fake_editor)

    orch = PostingOrchestrator(env_config=_FakeEnv())
    return orch, fake_editor, fake_login


def test_login_failure_returns_false_and_does_not_reach_editor(monkeypatch):
    orch, fake_editor, fake_login = _patched_orchestrator(monkeypatch, login_result=False)
    ok = orch.open_and_login("test_blog", account={"id": "a", "pw": "b", "blog_id": "test_blog"})
    assert ok is False
    fake_editor.navigate_to_editor.assert_not_called()


def test_login_success_reaches_editor(monkeypatch):
    orch, fake_editor, fake_login = _patched_orchestrator(monkeypatch, login_result=True)
    ok = orch.open_and_login("test_blog", account={"id": "a", "pw": "b", "blog_id": "test_blog"})
    assert ok is True
    fake_editor.navigate_to_editor.assert_called_once_with("test_blog")


def test_selector_failure_propagates_without_silent_retry_loop(monkeypatch):
    """에디터 셀렉터(예: 제목 입력란)를 못 찾아 예외가 나면, 오케스트레이터가
    조용히 삼키거나 무한 재시도하지 않고 그대로 예외를 올려 상위(웹서버)가
    '안전하게 중단'하고 사용자에게 알릴 수 있게 한다."""
    orch, fake_editor, _ = _patched_orchestrator(monkeypatch, login_result=True)
    orch.open_and_login("test_blog", account={"id": "a", "pw": "b", "blog_id": "test_blog"})

    fake_editor.input_title.side_effect = TimeoutException("title selector not found")
    with pytest.raises(TimeoutException):
        orch.write_content("제목", [{"heading": "h", "body": "b"}], [])
    assert fake_editor.input_title.call_count == 1  # 오케스트레이터 자체는 재시도를 추가하지 않는다


def test_cancel_before_save_skips_save_call(monkeypatch):
    orch, fake_editor, _ = _patched_orchestrator(monkeypatch, login_result=True)
    orch.open_and_login("test_blog", account={"id": "a", "pw": "b", "blog_id": "test_blog"})
    orch.cancel()
    ok = orch.save_post()
    assert ok is False
    fake_editor.save.assert_not_called()


def test_orchestrator_has_no_publish_method():
    """이 오케스트레이터에는 발행(공개 게시)을 수행하는 메서드가 존재하지 않는다."""
    public_methods = [m for m in dir(PostingOrchestrator) if not m.startswith("_")]
    for name in public_methods:
        assert "publish" not in name.lower()
        assert "발행" not in name


def test_save_post_only_calls_editor_save(monkeypatch):
    orch, fake_editor, _ = _patched_orchestrator(monkeypatch, login_result=True)
    orch.open_and_login("test_blog", account={"id": "a", "pw": "b", "blog_id": "test_blog"})
    orch.human_pacing = False  # 체류시간 대기 스킵
    fake_editor.save.return_value = True
    ok = orch.save_post()
    assert ok is True
    fake_editor.save.assert_called_once()
