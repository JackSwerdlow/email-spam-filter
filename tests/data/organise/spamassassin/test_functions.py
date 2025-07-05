"""Tests for the SpamAssassin data organisation module."""

from __future__ import annotations

import typing

import pytest

from email_spam_filter.data.organise.spamassassin.functions import organise_spamassassin_data

if typing.TYPE_CHECKING:
    import pathlib


@pytest.fixture
def raw_external_spamassassin_path_fixture(tmp_path: pathlib.Path) -> pathlib.Path:
    external = tmp_path / "external"
    ham_dir = external / "easy_ham_2003"
    spam_dir = external / "spam_2003"
    ham_dir.mkdir(parents=True)
    spam_dir.mkdir()
    for num in range(1, 3):
        (ham_dir / f"ham{num}").write_text(f"Subject: ham {num}\n\nBody")
    for num in range(1, 4):
        (spam_dir / f"spam{num}").write_text(f"Subject: spam {num}\n\nBody")
    return external


@pytest.fixture
def raw_spamassassin_path_fixture(tmp_path: pathlib.Path) -> tuple[pathlib.Path, pathlib.Path]:
    return tmp_path / "ham_spamassassin", tmp_path / "spam_spamassassin"


class TestOrganiseSpamAssassinData:
    @staticmethod
    def test_successful_run(
        raw_external_spamassassin_path_fixture: pathlib.Path,
        raw_spamassassin_path_fixture: tuple[pathlib.Path, pathlib.Path],
    ) -> None:
        raw_ham_path, raw_spam_path = raw_spamassassin_path_fixture
        organise_spamassassin_data(
            external_path=raw_external_spamassassin_path_fixture,
            raw_ham_path=raw_ham_path,
            raw_spam_path=raw_spam_path,
        )
        ham_files = sorted(p.name for p in raw_ham_path.iterdir())
        assert ham_files == ["1_ham.eml", "2_ham.eml"]
        spam_files = sorted(p.name for p in raw_spam_path.iterdir())
        assert spam_files == ["1_spam.eml", "2_spam.eml", "3_spam.eml"]
        assert (raw_ham_path / "1_ham.eml").read_text().startswith("Subject: ham 1")
        assert (raw_spam_path / "3_spam.eml").read_text().startswith("Subject: spam 3")

    @staticmethod
    @pytest.mark.parametrize(
        ("external", "raw_ham", "raw_spam"),
        (
            (None, "ham", "spam"),
            ("external", None, "spam"),
            ("external", "ham", None),
        ),
    )
    def test_missing_path_arg(
        tmp_path: pathlib.Path,
        external: str | None,
        raw_ham: str | None,
        raw_spam: str | None,
    ) -> None:
        def _path(name: str | None) -> pathlib.Path | None:
            return tmp_path / name if isinstance(name, str) else None

        with pytest.raises(ValueError, match="All arguments must be valid pathlib.Path instances"):
            organise_spamassassin_data(
                external_path=_path(external),
                raw_ham_path=_path(raw_ham),
                raw_spam_path=_path(raw_spam),
            )

    @staticmethod
    def test_missing_external_data(
        tmp_path: pathlib.Path, raw_spamassassin_path_fixture: tuple[pathlib.Path, pathlib.Path]
    ) -> None:
        bad_external = tmp_path / "missing_data"
        raw_ham, raw_spam = raw_spamassassin_path_fixture

        with pytest.raises(FileNotFoundError, match="SpamAssassin data not found"):
            organise_spamassassin_data(
                external_path=bad_external,
                raw_ham_path=raw_ham,
                raw_spam_path=raw_spam,
            )

    @staticmethod
    def test_incorrect_subfolder_name(
        tmp_path: pathlib.Path,
        raw_spamassassin_path_fixture: tuple[pathlib.Path, pathlib.Path],
    ) -> None:
        external = tmp_path / "external"
        (external / "bad_subfolder").mkdir(parents=True)
        raw_ham, raw_spam = raw_spamassassin_path_fixture

        with pytest.raises(
            FileNotFoundError,
            match="Incorrect folder 'bad_subfolder' in SpamAssassin external data.",
        ):
            organise_spamassassin_data(
                external_path=external,
                raw_ham_path=raw_ham,
                raw_spam_path=raw_spam,
            )
