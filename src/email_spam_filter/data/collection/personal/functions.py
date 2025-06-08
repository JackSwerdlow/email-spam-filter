"""Functions for connecting to email client, retrieving messages, and saving raw data."""

from __future__ import annotations

import imaplib
import logging
import ssl
import typing

import keyring

from email_spam_filter.common import paths
from email_spam_filter.common.constants import (
    FOLDER_MAP,
    IMAP_HOST,
    KEYRING_SERVICE,
    USER_EMAIL,
)

if typing.TYPE_CHECKING:
    import collections.abc
    import pathlib

logger = logging.getLogger(__name__)


def get_imap_password() -> str:
    """Retrieve the IMAP password for the configured user from the system keyring.

    Returns:
        The IMAP password associated with the configured email.
    """
    logger.info("Retrieving IMAP password from keyring for user: %s", USER_EMAIL)
    try:
        password = keyring.get_password(KEYRING_SERVICE, USER_EMAIL)
    except keyring.errors.NoKeyringError as exc:
        error_msg = (
            "No functional keyring backend. Install `keyrings.alt` or another backend, then run:\n"
            f"   python -m keyring set {KEYRING_SERVICE} {USER_EMAIL}"
        )
        raise RuntimeError(error_msg) from exc

    if not password:
        error_msg = (
            "IMAP password not found in keyring. Run:\n"
            f"   python -m keyring set {KEYRING_SERVICE} {USER_EMAIL}"
        )
        raise RuntimeError(error_msg)
    logger.info("Successfully retrieved IMAP password.")
    return password


def fetch_folder(
    imap: imaplib.IMAP4_SSL,
    folder: str,
    label: str,
    limit: int | None = None,
) -> collections.abc.Iterator[tuple[str, bytes, str]]:
    """Yield raw messages from an IMAP folder as (uid, raw_bytes, label).

    Args:
        imap: An authenticated IMAP4_SSL client.
        folder: The name of the IMAP folder to select (e.g., 'INBOX').
        label: A short label to attach to each message (e.g., 'inbox', 'spam').
        limit: Maximum number of messages to fetch (most recent). If None, fetch all.

    Yields:
        Tuples of (uid, raw_bytes, label).
    """
    logger.info("Selecting folder: '%s' (label: %s)...", folder, label)

    imap.select(folder, readonly=True)
    try:
        status, data = imap.search(None, "ALL")
    except imaplib.IMAP4.error:
        logger.warning("Failed to find folder '%s'. Skipping.", folder)
        return

    uids = data[0].split()
    if limit is not None:
        uids = uids[-limit:]

    logger.info("Found %d messages in folder: '%s'.", len(uids), folder)

    for uid in uids:
        status, msg_data = imap.fetch(uid, "(RFC822)")
        if status != "OK" or not msg_data or not msg_data[0]:
            logger.warning("Failed to fetch message UID %s in folder '%s'.", uid.decode(), folder)
            continue
        raw = typing.cast("tuple[bytes, bytes]", msg_data[0])[1]
        yield uid.decode(), raw, label


def save_raw_email(
    uid: str, raw_bytes: bytes, label: str, path: pathlib.Path = paths.RAW_DIR
) -> None:
    """Save raw email bytes to disk under the appropriate label subdirectory.

    Args:
        uid: The message UID identifier.
        raw_bytes: The raw RFC822 message contents.
        label: The folder label, used both in the filename and subdirectory.
        path: Path to the directory where raw emails will be saved.
    """
    target_dir = path / f"{label}_personal"
    target_dir.mkdir(parents=True, exist_ok=True)
    (target_dir / f"{uid}_{label}.eml").write_bytes(raw_bytes)


def fetch_and_save_emails(limit: int | None = None, *, path: pathlib.Path = paths.RAW_DIR) -> None:
    """Fetch and save messages from all folders defined in the user-defined FOLDER_MAP.

    Args:
        limit: Maximum number of messages to fetch (most recent). If None, fetch all.
        path: Path to the directory where raw emails will be saved. (Default: `paths.RAW_DIR`)
    """
    logger.info("Starting email download process.")
    if USER_EMAIL == "your_username@example.com":
        error_message = "USER_EMAIL is not configured. Please edit your `.env` file."
        raise RuntimeError(error_message)

    password = get_imap_password()
    ssl_ctx = ssl.create_default_context()

    with imaplib.IMAP4_SSL(IMAP_HOST, ssl_context=ssl_ctx) as imap:
        logger.info("Logging in to IMAP server '%s' as '%s'.", IMAP_HOST, USER_EMAIL)
        imap.login(USER_EMAIL, password)

        for folder, label in FOLDER_MAP.items():
            for uid, raw, lbl in fetch_folder(imap, folder, label, limit):
                save_raw_email(uid, raw, lbl, path)
        logger.info("Logging out from IMAP server.")
        imap.logout()
    logger.info("Email download process completed.")
