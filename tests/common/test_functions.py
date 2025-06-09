"""Tests for functions for the common module."""

from __future__ import annotations

import typing

import pytest

from email_spam_filter.common.functions import load_user_config

if typing.TYPE_CHECKING:
    import pathlib


@pytest.fixture
def clear_load_user_config_cache() -> None:
    load_user_config.cache_clear()


@pytest.fixture
def user_config_fixture(tmp_path: pathlib.Path) -> pathlib.Path:
    config_data = [
        "USER_EMAIL=test@example.com",
        "IMAP_HOST=imap.test.com",
        "KEYRING_SERVICE=test-service",
        'FOLDER_MAP={"INBOX":"inbox","Spam":"spam"}',
    ]
    config_path = tmp_path / ".env"
    config_path.write_text("\n".join(config_data))
    return config_path


@pytest.mark.usefixtures("clear_load_user_config_cache")
class TestLoadUserConfig:
    @staticmethod
    def test_valid_load_user_config(
        user_config_fixture: pathlib.Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.chdir(user_config_fixture.parent)
        for var in ("USER_EMAIL", "IMAP_HOST", "KEYRING_SERVICE", "FOLDER_MAP"):
            monkeypatch.delenv(var, raising=False)
        config = load_user_config()
        assert config.user_email == "test@example.com"
        assert config.imap_host == "imap.test.com"
        assert config.keyring_service == "test-service"
        assert config.folder_map["INBOX"] == "inbox"
        assert config.folder_map["Spam"] == "spam"

    @staticmethod
    def test_missing_load_user_config(
        tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.chdir(tmp_path)
        for var in ("USER_EMAIL", "IMAP_HOST", "KEYRING_SERVICE", "FOLDER_MAP"):
            monkeypatch.delenv(var, raising=False)
        with pytest.raises(RuntimeError, match="Missing configuration values: "):
            load_user_config()
