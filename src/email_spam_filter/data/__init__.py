"""Data ingestion, pre-processing, and labelling utilities for the email-spam-filter project.

Modules:
    collection: Source-specific data collection utilities for acquiring external datasets.
    organise: Source-specific pre-processing utilities for external datasets.
"""

from __future__ import annotations

__all__ = ("collection", "organise")

from email_spam_filter.data import (
    collection,
    organise,
)
