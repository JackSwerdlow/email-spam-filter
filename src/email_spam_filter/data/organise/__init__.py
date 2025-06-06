"""Source-specific pre-processing utilities for external datasets.

Modules:
    spamassassin: Pre-processing utilities for the SpamAssassin dataset.
    trec: Pre-processing utilities for the TREC Public Spam Corpus.
"""

from __future__ import annotations

__all__ = (
    "DATASET_MODULES",
    "spamassassin",
    "trec",
)

from email_spam_filter.data.organise import spamassassin, trec

DATASET_MODULES = {
    "TREC": trec.organise_trec_data,
    "SpamAssassin": spamassassin.organise_spamassassin_data,
}
