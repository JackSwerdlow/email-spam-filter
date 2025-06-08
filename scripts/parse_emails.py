"""Script to parse raw .eml files from all datasets and serialize them as structured EmailData.

Before running:
    1. Ensure all datasets are downloaded and organised in the expected folders:
       - trec:          data/raw/trec_ham, data/raw/trec_spam
       - spamassassin:  data/raw/spamassassin_ham, data/raw/spamassassin_spam
       - personal:      data/raw/personal_inbox, data/raw/personal_spam

    2. Install dev dependencies via Poetry (if not already done):
       > poetry install --with dev

Usage:
    > python parse_emails.py

This will serialize parsed EmailData to Parquet files in:
    - data/processed/{dataset_name}_processed
"""

from __future__ import annotations

from email_spam_filter.common import logger, paths
from email_spam_filter.data.io.functions import create_email_data, serialize_email_data

if __name__ == "__main__":
    logger()
    for dataset in paths.DATASET_PATHS.values():
        for field_name, folder in dataset.model_dump().items():
            if field_name.startswith("raw_") and folder:
                if not folder.exists():
                    print(f"Cannot find {folder}")
                    continue
                eml_paths = sorted(folder.glob("*.eml"))
                email_data = [create_email_data(path) for path in eml_paths]
                if dataset.processed:
                    serialize_email_data(email_data, path=dataset.processed)
