"""Global constants and user configurations values."""

from __future__ import annotations

from email_spam_filter.common.functions import load_user_config

CONFIG = load_user_config()

USER_EMAIL: str = CONFIG.user_email
"""Email address used to log in to the IMAP server."""

IMAP_HOST: str = CONFIG.imap_host
"""IMAP server host for the email provider."""

KEYRING_SERVICE: str = CONFIG.keyring_service
"""Service name used by keyring for password retrieval."""

FOLDER_MAP: dict[str, str] = CONFIG.folder_map
"""Mapping of IMAP folder names to short local labels."""
