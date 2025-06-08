"""Creates a default .env file that must be editied by user before using `fetch_imap.inbox.py`.

Usage:
    python -m email_spam_filter.setup
"""

from __future__ import annotations

import pathlib

import dotenv


def create_default_env_file() -> None:
    """Create a default .env file containing placeholder configuration values."""
    env_path = pathlib.Path(".env").resolve()
    env_path.touch(mode=0o600, exist_ok=False)
    dotenv.set_key(
        env_path,
        key_to_set="USER_EMAIL",
        value_to_set="your_username@example.com",
    )
    dotenv.set_key(
        env_path,
        key_to_set="IMAP_HOST",
        value_to_set="imap.virginmedia.com",
    )
    dotenv.set_key(
        env_path,
        key_to_set="KEYRING_SERVICE",
        value_to_set="virgin-imap",
    )
    dotenv.set_key(
        env_path,
        key_to_set="FOLDER_MAP",
        value_to_set='{"INBOX": "inbox", "Spam": "spam"}',
    )
