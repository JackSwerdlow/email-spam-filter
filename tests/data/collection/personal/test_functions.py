"""Tests for functions for the personal data collection module."""

from __future__ import annotations

import unittest.mock

import keyring
import pytest

from email_spam_filter.data.collection.personal.functions import get_imap_password


class TestGetIMAPPassword:
    @staticmethod
    @unittest.mock.patch(
        "email_spam_filter.data.collection.personal.functions.keyring.get_password"
    )
    def test_success(mock_get_password: unittest.mock.MagicMock) -> None:
        mock_get_password.return_value = "secure-password"
        assert get_imap_password() == "secure-password"

    @staticmethod
    @unittest.mock.patch(
        "email_spam_filter.data.collection.personal.functions.keyring.get_password"
    )
    def test_missing_password_raises(mock_get_password: unittest.mock.MagicMock) -> None:
        mock_get_password.return_value = None
        with pytest.raises(RuntimeError, match="IMAP password not found in keyring"):
            get_imap_password()

    @staticmethod
    @unittest.mock.patch(
        "email_spam_filter.data.collection.personal.functions.keyring.get_password",
        side_effect=keyring.errors.NoKeyringError("No backend found"),
    )
    def test_keyring_error(mock_get_password: unittest.mock.MagicMock) -> None:
        mock_get_password.return_value = None
        with pytest.raises(RuntimeError, match="No functional keyring backend"):
            get_imap_password()
