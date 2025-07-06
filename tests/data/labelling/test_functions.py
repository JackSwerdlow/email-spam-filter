"""Tests for functions for the data labelling module."""

from __future__ import annotations

import typing

import pytest

from email_spam_filter.data.labelling.functions import (
    _label_single_email,
    _load_existing_labels,
    _save_labels,
)

if typing.TYPE_CHECKING:
    import pathlib

    import pytest_mock

    from email_spam_filter.common import EmailData


@pytest.fixture
def mock_emaildata_fixture(mocker: pytest_mock.MockerFixture) -> EmailData:
    mock = mocker.MagicMock(
        id=101,
        from_addr="tester@example.net",
        n_links=0,
        has_attach=False,
        subject="Hello world",
        body="<p>Hi</p>",
        spec=["id", "from_addr", "n_links", "has_attach", "subject", "body"],
    )
    return typing.cast("EmailData", mock)


@pytest.fixture
def label_json_path(tmp_path: pathlib.Path) -> pathlib.Path:
    return tmp_path / "labels.json"


class TestLabelling:
    @staticmethod
    def test_first_time_load(label_json_path: pathlib.Path) -> None:
        labels = _load_existing_labels(label_json_path)
        assert labels == {}

    @staticmethod
    def test_save_and_reload(label_json_path: pathlib.Path) -> None:
        original = {"10": 1, "2": 2, "35": 3}
        _save_labels(label_json_path, original)
        loaded = _load_existing_labels(label_json_path)
        assert loaded == original

    @staticmethod
    @pytest.mark.parametrize(("user_input", "expected_label"), (("1", 1), ("2", 2), ("3", 3)))
    def test_label_single_email(
        user_input: str,
        expected_label: int,
        mock_emaildata_fixture: EmailData,
        label_json_path: pathlib.Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        labels: dict[str, int] = {}
        monkeypatch.setattr("builtins.input", lambda _: user_input)
        proceed = _label_single_email(mock_emaildata_fixture, labels, label_json_path)
        assert proceed is True
        assert labels == {str(mock_emaildata_fixture.id): expected_label}
        assert _load_existing_labels(label_json_path) == labels

    @staticmethod
    def test_label_single_email_quit(
        mock_emaildata_fixture: EmailData,
        label_json_path: pathlib.Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        labels: dict[str, int] = {}
        monkeypatch.setattr("builtins.input", lambda _: "q")
        proceed = _label_single_email(mock_emaildata_fixture, labels, label_json_path)
        assert proceed is False
        assert labels == {}
        assert not label_json_path.exists()

    @staticmethod
    def test_label_single_email_invalid_input(
        mock_emaildata_fixture: EmailData,
        label_json_path: pathlib.Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        labels: dict[str, int] = {}
        monkeypatch.setattr("builtins.input", lambda _: "xyz")
        proceed = _label_single_email(mock_emaildata_fixture, labels, label_json_path)
        assert proceed is True
        assert labels == {}
        assert not label_json_path.exists()
