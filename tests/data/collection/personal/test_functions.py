"""Tests for functions for the personal data collection module."""

from __future__ import annotations

import imaplib
import pathlib
import typing

import keyring
import pytest

from email_spam_filter.data.collection.personal.functions import (
    fetch_folder,
    get_imap_password,
    save_raw_email,
)

if typing.TYPE_CHECKING:
    import pytest_mock


@pytest.fixture
def eml_fixture() -> bytes:
    path = pathlib.Path(__file__).parent / "example_email.eml"
    return path.read_bytes()


@pytest.fixture
def folder_fixture() -> str:
    return "INBOX"


@pytest.fixture
def label_fixture() -> str:
    return "inbox"


@pytest.fixture
def imap_fixture(mocker: pytest_mock.MockerFixture, eml_fixture: bytes) -> imaplib.IMAP4_SSL:
    imap_fixture = mocker.MagicMock(spec=imaplib.IMAP4_SSL)
    imap_fixture.select.return_value = ("OK", [b"1"])
    imap_fixture.search.return_value = ("OK", [b"1"])
    imap_fixture.fetch.return_value = (
        "OK",
        [(b"1 (RFC822 {%d})" % len(eml_fixture), eml_fixture), b")"],
    )
    return typing.cast("imaplib.IMAP4_SSL", imap_fixture)


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


def test_fetch_folder(
    imap_fixture: imaplib.IMAP4_SSL, folder_fixture: str, label_fixture: str
) -> None:
    results = list(fetch_folder(imap_fixture, folder_fixture, label_fixture))
    assert len(results) == 1

    uid, raw_bytes, label = results[0]
    assert uid == "1"
    assert isinstance(raw_bytes, bytes)
    assert raw_bytes.startswith(b"Return-Path: <john_mcafee@examplemail.com>")
    assert label == label_fixture


def test_save_raw_email(eml_fixture: bytes, label_fixture: str, tmp_path: pathlib.Path) -> None:
    uid = "123"
    save_raw_email(uid, eml_fixture, label_fixture, path=tmp_path)
    test_file = tmp_path / "inbox_personal" / "123_inbox.eml"
    assert test_file.exists()
