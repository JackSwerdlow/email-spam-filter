"""Paths to important project resources."""

from __future__ import annotations

from pathlib import Path

from email_spam_filter.common.constants import FOLDER_MAP
from email_spam_filter.common.containers import DatasetPaths

BASE_DIR = Path(__file__).resolve().parents[3]
"""Base directory of the project."""

CONFIG_PATH = BASE_DIR / "user_config.yml"
"""Path to the user config file."""

DATA_DIR = BASE_DIR / "data"
"""Path to the data folder."""

LABELS_DIR = DATA_DIR / "labels"
"""Path to the labels data folder."""

PROCESSED_DIR = DATA_DIR / "processed"
"""Path to the processed data folder."""

RAW_DIR = DATA_DIR / "raw"
"""Path to the raw data folder."""

RAW_EXTERNAL_DIR = DATA_DIR / "raw_external"
"""Path to the raw external data folder. (e.g. TREC, SpamAssassin etc.)"""

TREC_PATHS: DatasetPaths = DatasetPaths(
    external=RAW_EXTERNAL_DIR / "trec",
    raw_ham=RAW_DIR / "trec_ham",
    raw_spam=RAW_DIR / "trec_spam",
    raw_inbox=None,
    processed=PROCESSED_DIR / "trec_processed.parquet",
    labels=None,
)
"""Paths for the [TREC Public Spam Corpus dataset](https://plg.uwaterloo.ca/cgi-bin/cgiwrap/gvcormac/foo)."""

SPAM_ASSASSIN_PATHS = DatasetPaths(
    external=RAW_EXTERNAL_DIR / "spamassassin",
    raw_ham=RAW_DIR / "spamassassin_ham",
    raw_spam=RAW_DIR / "spamassassin_spam",
    raw_inbox=None,
    processed=PROCESSED_DIR / "spamassassin_processed.parquet",
    labels=None,
)
"""Paths for the [SpamAssassin Public Spam Corpus dataset](https://spamassassin.apache.org/old/publiccorpus/)."""

PERSONAL_PATHS = DatasetPaths(
    external=RAW_EXTERNAL_DIR / "personal",
    processed=PROCESSED_DIR / "personal_processed.parquet",
    labels=None,
    **{f"raw_{label}": RAW_DIR / f"personal_{label}" for label in FOLDER_MAP.values()},
)
"""Paths for the users personal email data."""

DATASET_PATHS = {
    "trec": TREC_PATHS,
    "spamassassin": SPAM_ASSASSIN_PATHS,
    "personal": PERSONAL_PATHS,
}
