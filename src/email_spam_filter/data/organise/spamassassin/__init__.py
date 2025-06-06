"""Pre-processing utilities for the SpamAssassin dataset.

Modules:
    functions: Functions for loading and standardising the SpamAssassin dataset.
"""

from __future__ import annotations

__all__ = ("organise_spamassassin_data",)

from email_spam_filter.data.organise.spamassassin.functions import (
    organise_spamassassin_data,
)
