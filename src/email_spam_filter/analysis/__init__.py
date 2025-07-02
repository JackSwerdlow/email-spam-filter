"""Analysis tools for evaluating the email-spam-filter project.

Modules:
    functions: General-purpose analysis utilities for data inspection and evaluation.
"""

from __future__ import annotations

__all__ = (
    "get_model_features",
    "predicted_email_summary",
    "show_email_features",
)

from email_spam_filter.analysis.functions import (
    get_model_features,
    predicted_email_summary,
    show_email_features,
)
