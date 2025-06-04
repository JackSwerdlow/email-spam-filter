"""Tests for functions for the common module."""

from __future__ import annotations

import typing

import pytest
import yaml

from email_spam_filter.common.functions import load_user_config

if typing.TYPE_CHECKING:
    import pathlib


@pytest.fixture
def user_config_fixture(tmp_path: pathlib.Path) -> pathlib.Path:
    config_data = {
        "user_email": "test@example.com",
        "imap_host": "imap.test.com",
        "keyring_service": "test-service",
        "folder_map": {"INBOX": "inbox", "Spam": "spam"},
    }
    config_path = tmp_path / "user_config.yml"
    config_path.write_text(yaml.dump(config_data))
    return config_path


class TestLoadUserConfig:
    @staticmethod
    def test_valid_load_user_config(user_config_fixture: pathlib.Path) -> None:
        config = load_user_config(user_config_fixture)
        assert config["user_email"] == "test@example.com"
        assert config["imap_host"] == "imap.test.com"
        assert config["keyring_service"] == "test-service"
        assert config["folder_map"]["INBOX"] == "inbox"
        assert config["folder_map"]["Spam"] == "spam"

    @staticmethod
    def test_missing_load_user_config(tmp_path: pathlib.Path) -> None:
        missing_path = tmp_path / "does_not_exist.yml"
        with pytest.raises(FileNotFoundError, match="Missing user_config.yml file."):
            load_user_config(missing_path)
