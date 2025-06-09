"""Input/output utilities for reading, writing, and processing email data.

Modules:
    functions: Utilities for reading, writing, and processing email-related data.
"""

from __future__ import annotations

__all__ = (
    "create_email_data",
    "deserialize_email_data",
    "parse_email_message",
    "serialize_email_data",
)

from email_spam_filter.data.io.functions import (
    create_email_data,
    deserialize_email_data,
    parse_email_message,
    serialize_email_data,
)
