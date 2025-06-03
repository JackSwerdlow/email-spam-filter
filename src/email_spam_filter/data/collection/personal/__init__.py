"""Scripts and utilities for collecting personal email data.

Modules:
    functions: Functions for connecting to email client, retrieving messages, and saving raw data.
"""

from __future__ import annotations

__all__ = ("fetch_and_save_emails",)

from email_spam_filter.data.collection.personal.functions import (
    fetch_and_save_emails,
)
