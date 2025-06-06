"""Data ingestion, pre-processing, and labelling utilities for the email-spam-filter project.

Modules:
    collection: Source-specific data collection utilities for acquiring external datasets.
    io: Input/output utilities for reading, writing, and processing email data.
    organise: Source-specific pre-processing utilities for external datasets.
"""

from __future__ import annotations

__all__ = (
    "collection",
    "io",
    "organise",
)

from email_spam_filter.data import (
    collection,
    io,
    organise,
)
