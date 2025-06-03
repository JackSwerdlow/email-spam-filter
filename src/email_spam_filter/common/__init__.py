"""Common utilities and shared data structures for the email-spam-filter project.

Modules:
    constants: Global constants and user configurations values.
    functions: Generic utility functions.
    paths: Paths to important project resources.
"""

from __future__ import annotations

__all__ = (
    "FOLDER_MAP",
    "IMAP_HOST",
    "KEYRING_SERVICE",
    "USER_EMAIL",
    "logger",
    "paths",
    "simple_logger",
)

from email_spam_filter.common import paths
from email_spam_filter.common.constants import (
    FOLDER_MAP,
    IMAP_HOST,
    KEYRING_SERVICE,
    USER_EMAIL,
)
from email_spam_filter.common.functions import (
    logger,
    simple_logger,
)
