"""Functions for loading and standardising the SpamAssassin dataset."""

from __future__ import annotations

import logging
import shutil
import typing

from email_spam_filter.common import paths

if typing.TYPE_CHECKING:
    import pathlib

logger = logging.getLogger(__name__)


def organise_spamassassin_data(
    external_path: pathlib.Path = paths.SPAM_ASSASSIN_PATHS.external,
    raw_ham_path: pathlib.Path = paths.SPAM_ASSASSIN_PATHS.raw_ham,
    raw_spam_path: pathlib.Path = paths.SPAM_ASSASSIN_PATHS.raw_spam,
) -> None:
    """Reads the SpamAssassin external folders and copies each file into a ham or spam folder.

    Args:
        external_path: Path to the external sourced raw Spam Assassin dataset.
            (Default: `paths.SPAM_ASSASSIN_PATHS.raw_external`)
        raw_ham_path: Path to the folder where the ham .eml files will be stored.
            (Default: `paths.SPAM_ASSASSIN_PATHS.raw_ham`)
        raw_spam_path: Path to the folder where the spam .eml files will be stored.
            (Default: `paths.SPAM_ASSASSIN_PATHS.raw_spam`)
    """
    logger.info("Starting SpamAssassin data organisation...")
    logger.info("Creating directories...")
    raw_ham_path.mkdir(parents=True, exist_ok=True)
    raw_spam_path.mkdir(parents=True, exist_ok=True)

    logger.info("Organising data...")
    if not external_path.is_dir():
        error_message = (
            f"SpamAssassin data not found at {external_path!r}. "
            "Please verify that the dataset directory exists and contains subfolders "
            "containing either the words 'ham' or 'spam'. You can download the correct data from: https://spamassassin.apache.org/old/publiccorpus/"
        )
        raise FileNotFoundError(error_message)

    missing_files: list[pathlib.Path] = []
    ham_uid: int = 0
    spam_uid: int = 0

    for subdir in sorted(external_path.iterdir()):
        subdir_name = subdir.name.lower()
        if not subdir.is_dir() or not any(tag in subdir_name for tag in ("ham", "spam")):
            error_message = f"Incorrect folder '{subdir.name}' in SpamAssassin external data."
            raise FileNotFoundError(error_message)

        label = "spam" if "spam" in subdir_name else "ham"
        for src in sorted(subdir.iterdir()):
            if not src.is_file():
                missing_files.append(src)
                logger.debug("[!] Skipping invalid or non-file entry: %s", src)
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

    logger.info("SpamAssassin data organisation complete.")
