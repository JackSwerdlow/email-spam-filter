"""Repository for the email-spam-filter project.

Modules:
    analysis: Analysis tools for evaluating the email-spam-filter project.
    common: Common utilities and shared data structures for the email-spam-filter project.
    data: Data ingestion, pre-processing, and labelling utilities for the email-spam-filter project.
    ml: Machine learning components for the email-spam-filter project.
"""

from __future__ import annotations

__all__ = (
    "analysis",
    "common",
    "data",
    "ml",
)

from email_spam_filter import (
    analysis,
    common,
    data,
    ml,
)
