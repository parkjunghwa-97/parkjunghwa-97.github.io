"""7단계 테스트 9, 11: 발행 함수 차단 / 로그 비밀정보 마스킹."""
import os

import pytest

import config.safety as safety
from utils.mask import mask_secrets


def test_dry_run_default_true_when_unset(monkeypatch):
    monkeypatch.delenv("DRY_RUN", raising=False)
    import importlib
    importlib.reload(safety)
    assert safety.DRY_RUN is True
    importlib.reload(safety)  # restore module state for other tests


def test_allow_publish_is_hardcoded_false_even_if_env_says_true(monkeypatch):
    monkeypatch.setenv("ALLOW_PUBLISH", "true")
    import importlib
    importlib.reload(safety)
    assert safety.ALLOW_PUBLISH is False
    monkeypatch.delenv("ALLOW_PUBLISH", raising=False)
    importlib.reload(safety)


def test_assert_publish_forbidden_always_raises():
    with pytest.raises(RuntimeError):
        safety.assert_publish_forbidden()


def test_enforce_local_host_rejects_external():
    with pytest.raises(RuntimeError):
        safety.enforce_local_host("0.0.0.0")
    assert safety.enforce_local_host("127.0.0.1") == "127.0.0.1"


def test_enforce_single_post_run():
    safety.enforce_single_post_run(1)  # ok
    with pytest.raises(RuntimeError):
        safety.enforce_single_post_run(2)


def test_bulk_and_scheduled_features_disabled():
    assert safety.BULK_MODE_ENABLED is False
    assert safety.SCHEDULED_MODE_ENABLED is False
    assert safety.AUTO_COMMENT_ENABLED is False
    assert safety.AUTO_LIKE_ENABLED is False
    assert safety.AUTO_NEIGHBOR_ADD_ENABLED is False
    assert safety.CAPTCHA_BYPASS_ENABLED is False
    assert safety.DETECTION_EVASION_FEATURES_ENABLED is False


def test_image_extension_and_size_validation():
    assert safety.validate_image_extension("photo.jpg") is True
    assert safety.validate_image_extension("virus.exe") is False
    assert safety.validate_image_size(1024) is True
    assert safety.validate_image_size(safety.MAX_IMAGE_SIZE_MB * 1024 * 1024 + 1) is False


def test_mask_secrets_hides_known_env_values(monkeypatch):
    monkeypatch.setenv("NAVER_PW", "SuperSecretPassword123")
    monkeypatch.setenv("CLAUDE_API_KEY", "sk-ant-abcdefghijklmnopqrstuvwxyz")
    text = "로그인 실패: pw=SuperSecretPassword123, key=sk-ant-abcdefghijklmnopqrstuvwxyz 확인 필요"
    masked = mask_secrets(text)
    assert "SuperSecretPassword123" not in masked
    assert "sk-ant-abcdefghijklmnopqrstuvwxyz" not in masked
    assert "MASKED" in masked


def test_mask_secrets_leaves_normal_text_untouched():
    text = "임시저장 완료! 제목 길이 32자"
    assert mask_secrets(text) == text
