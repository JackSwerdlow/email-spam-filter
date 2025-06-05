"""Functions for loading and standardising the TREC Public Spam Corpus."""

from __future__ import annotations

import logging
import shutil
import typing

from email_spam_filter.common import paths

if typing.TYPE_CHECKING:
    import pathlib

logger = logging.getLogger(__name__)


def organise_trec_data(
    raw_external_path: pathlib.Path = paths.TREC_PATHS.raw_external,
    raw_ham_path: pathlib.Path = paths.TREC_PATHS.raw_ham,
    raw_spam_path: pathlib.Path = paths.TREC_PATHS.raw_spam,
) -> None:
    """Reads the TREC index and copies each file into a ham or spam folder.

    Args:
        raw_external_path: Path to the external sourced raw TREC dataset.
            (Default: `paths.TREC_PATHS.raw_external`)
        raw_ham_path: Path to the folder where the ham .eml files will be stored.
            (Default: `paths.TREC_PATHS.raw_ham`)
        raw_spam_path: Path to the folder where the spam .eml files will be stored.
            (Default: `paths.TREC_PATHS.raw_spam`)
    """
    logger.info("Starting TREC data organisation...")
    logger.info("Creating directories...")
    raw_ham_path.mkdir(parents=True, exist_ok=True)
    raw_spam_path.mkdir(parents=True, exist_ok=True)

    logger.info("Organising data...")
    index_path = raw_external_path / "full" / "index"
    if not index_path.is_file():
        error_message = (
            f"Index file not found at {index_path!r}. Please verify that the TREC "
            "dataset was unzipped correctly, the directory names are accurate, and a 'full' folder "
            "containing an 'index' file exists. You can download the correct data from: https://plg.uwaterloo.ca/cgi-bin/cgiwrap/gvcormac/foo"
        )
        raise FileNotFoundError(error_message)

    missing_files: list[pathlib.Path] = []
    ham_uid: int = 0
    spam_uid: int = 0

    with index_path.open() as idx_file:
        for line in idx_file:
            label, rel_path = line.strip().split(maxsplit=1)
            if label not in ("ham", "spam"):
                error_message = f"Invalid tag {label} in index"
                raise RuntimeError(error_message)
            src = (raw_external_path / "full" / rel_path).resolve()
            if not src.is_file():
                missing_files.append(src)
                logger.debug("[!] Data file missing: %s", src)
                continue
            if label == "ham":
                ham_uid += 1
                dest = raw_ham_path / f"{ham_uid}_ham.eml"
            elif label == "spam":
                spam_uid += 1
                dest = raw_spam_path / f"{spam_uid}_spam.eml"
            else:
                missing_files.append(src)
                logger.debug("[!] Unrecognised label for data file: %s", src)
            shutil.copy(str(src), str(dest))

    if missing_files:
        logger.warning(
            "Skipped %d invalid or missing files. Change logger level to DEBUG to view details.",
            len(missing_files),
        )

    logger.info("TREC data organisation complete.")
