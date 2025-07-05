"""Tests for the TREC data organisation module."""

from __future__ import annotations

import typing

import pytest

from email_spam_filter.data.organise.trec.functions import organise_trec_data

if typing.TYPE_CHECKING:
    import pathlib


@pytest.fixture
def raw_external_trec_path_fixture(tmp_path: pathlib.Path) -> pathlib.Path:
    external = tmp_path / "external"
    full_dir = external / "full"
    data_dir = external / "data"
    full_dir.mkdir(parents=True)
    (data_dir / "000").mkdir(parents=True)
    (data_dir / "001").mkdir(parents=True)
    (data_dir / "000" / "000").write_text("Subject: ham 1\n\nBody")
    (data_dir / "000" / "001").write_text("Subject: spam 1\n\nBody")
    (data_dir / "001" / "000").write_text("Subject: ham 2\n\nBody")
    (data_dir / "001" / "001").write_text("Subject: spam 2\n\nBody")
    (data_dir / "001" / "002").write_text("Subject: spam 3\n\nBody")
    index_lines = [
        "ham ../data/000/000",
        "spam ../data/000/001",
        "ham ../data/001/000",
        "spam ../data/001/001",
        "spam ../data/001/002",
    ]
    (full_dir / "index").write_text("\n".join(index_lines) + "\n")
    return external


@pytest.fixture
def raw_trec_path_fixture(tmp_path: pathlib.Path) -> tuple[pathlib.Path, pathlib.Path]:
    return tmp_path / "trec_ham", tmp_path / "trec_spam"


class TestOrganiseTrecData:
    @staticmethod
    def test_successful_run(
        raw_external_trec_path_fixture: pathlib.Path,
        raw_trec_path_fixture: tuple[pathlib.Path, pathlib.Path],
    ) -> None:
        raw_ham_path, raw_spam_path = raw_trec_path_fixture

        organise_trec_data(
            external_path=raw_external_trec_path_fixture,
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
            organise_trec_data(
                external_path=_path(external),
                raw_ham_path=_path(raw_ham),
                raw_spam_path=_path(raw_spam),
            )

    @staticmethod
    def test_missing_index_file(
        tmp_path: pathlib.Path, raw_trec_path_fixture: tuple[pathlib.Path, pathlib.Path]
    ) -> None:
        (tmp_path / "external" / "full").mkdir(parents=True)
        external = tmp_path / "external"
        raw_ham, raw_spam = raw_trec_path_fixture

        with pytest.raises(FileNotFoundError, match="Index file not found"):
            organise_trec_data(
                external_path=external,
                raw_ham_path=raw_ham,
                raw_spam_path=raw_spam,
            )

    @staticmethod
    def test_invalid_label_in_index(
        tmp_path: pathlib.Path, raw_trec_path_fixture: tuple[pathlib.Path, pathlib.Path]
    ) -> None:
        external = tmp_path / "external"
        (external / "full").mkdir(parents=True)
        (external / "full" / "index").write_text("INVALID ../data/000/000\n")
        raw_ham, raw_spam = raw_trec_path_fixture

        with pytest.raises(RuntimeError, match="Invalid tag INVALID in index"):
            organise_trec_data(
                external_path=external,
                raw_ham_path=raw_ham,
                raw_spam_path=raw_spam,
            )
