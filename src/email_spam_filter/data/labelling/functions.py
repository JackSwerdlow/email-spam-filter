"""Tools for assigning and storing labels for email samples."""

from __future__ import annotations

import json
import logging
import typing

from email_spam_filter.common import clean_html
from email_spam_filter.data.io import deserialize_email_data

if typing.TYPE_CHECKING:
    from pathlib import Path

    from email_spam_filter.common.containers import EmailData

logger = logging.getLogger(__name__)


def _load_existing_labels(path: Path) -> dict[str, int]:
    """Load existing email labels from a JSON file, if available.

    Args:
        path: Path to the JSON file containing email ID to label mappings.

    Returns:
        A dictionary mapping email IDs (as strings) to integer labels.
    """
    if path.exists():
        labels_dict: dict[str, int] = json.loads(path.read_text())
        return labels_dict
    logger.info("Labels JSON file not found, creating new labels dictionary at %s", path)
    return {}


def _save_labels(path: Path, labels: dict[str, int]) -> None:
    """Save the email label dictionary to a JSON file.

    Args:
        path: Destination path to save the labels.
        labels: A dictionary of email ID -> label mappings to save.
    """
    sorted_labels = dict(sorted(labels.items(), key=lambda x: int(x[0])))
    path.write_text(json.dumps(sorted_labels, indent=2))


def _label_single_email(email: EmailData, labels: dict[str, int], label_path: Path) -> bool:
    """Interactively label a single email and update the labels dictionary.

    Args:
        email: The EmailData object to be labelled.
        labels: Existing dictionary of email ID to label mappings.
        label_path: Path to the JSON file where labels are saved.

    Returns:
        False if the user chose to quit, True otherwise.
    """
    logger.info("Labelling email ID: %s", email.id)

    logger.info("%sSUMMARY%s", "=" * 34, "=" * 34)
    logger.info(
        "From: %s | Links: %s | Attachments: %s", email.from_addr, email.n_links, email.has_attach
    )
    logger.info("Subject: %s", email.subject)

    snippet = clean_html(email.body)[:500]
    logger.info("%sEMAIL SNIPPET%s\n%s ...", "=" * 31, "=" * 31, snippet)
    logger.info("=" * 75)
    choice = input("[1]=Ham  [2]=Spam  [3]=Unknown  [q]=Quit\n> ").strip().lower()

    if choice == "q":
        logger.info("User quit early.")
        return False
    if choice not in {"1", "2", "3"}:
        logger.warning("Invalid input. Skipping this email. Restart script to revisit.")
        return True

    labels[str(email.id)] = int(choice)
    _save_labels(label_path, labels)
    logger.info("Labelled email %s as %s", email.id, choice)
    return True


def run_labelling_session(email_path: Path | None, label_path: Path | None) -> None:
    """Launch an interactive session for labelling a set of emails.

    Args:
        email_path: Path to the input Parquet file containing email data.
        label_path: Path to the JSON file where labels will be saved.
    """
    if not email_path or not label_path:
        error_message = "Please ensure both input paths are correctly defined."
        raise TypeError(error_message)
    emails = deserialize_email_data(email_path)
    labels = _load_existing_labels(label_path)

    logger.info("Loaded %s existing labels.", len(labels))
    logger.info("%s emails remaining to label.", len(emails) - len(labels))

    for email in sorted(emails, key=lambda e: e.id):
        if str(email.id) in labels:
            continue
        if not _label_single_email(email, labels, label_path):
            break

    logger.info("Labelling session complete.")
    logger.info("Total labels saved: %s", len(labels))
