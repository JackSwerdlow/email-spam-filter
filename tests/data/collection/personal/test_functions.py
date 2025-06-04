"""Tests for functions for the personal data collection module."""

from __future__ import annotations

import typing

import keyring
import pytest

from email_spam_filter.data.collection.personal.functions import get_imap_password

if typing.TYPE_CHECKING:
    import pytest_mock


class TestGetIMAPPassword:
    @staticmethod
    def test_success(mocker: pytest_mock.MockerFixture) -> None:
        mocker.patch(
            "email_spam_filter.data.collection.personal.functions.keyring.get_password",
            return_value="secure-password",
        )
        assert get_imap_password() == "secure-password"

    @staticmethod
    def test_missing_password_raises(mocker: pytest_mock.MockerFixture) -> None:
        mocker.patch(
            "email_spam_filter.data.collection.personal.functions.keyring.get_password",
            return_value=None,
        )
        with pytest.raises(RuntimeError, match="IMAP password not found in keyring"):
            get_imap_password()

    @staticmethod
    def test_keyring_error(mocker: pytest_mock.MockerFixture) -> None:
        mocker.patch(
            "email_spam_filter.data.collection.personal.functions.keyring.get_password",
            side_effect=keyring.errors.NoKeyringError("No backend found"),
        )
        with pytest.raises(RuntimeError, match="No functional keyring backend"):
            get_imap_password()
