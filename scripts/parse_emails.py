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

    for dataset_name, dataset_paths in paths.DATASET_PATHS.items():
        print(f"\nProcessing dataset: {dataset_name}")

        for field_name, raw_folder in dataset_paths.model_dump().items():
            if not field_name.startswith("raw_") or not raw_folder:
                continue

            print(f"  Reading emails from: {raw_folder}")
            if not raw_folder.exists():
                print(f"  [!] Skipped: {field_name} Folder not found.")
                continue

            eml_paths = sorted(raw_folder.glob("*.eml"))
            if not eml_paths:
                print(f"  [!] Skipped: {field_name} No .eml files found.")
                continue

            print(f"  Parsing {len(eml_paths)} email(s)...")
            email_data = [create_email_data(path) for path in eml_paths]

            if dataset_paths.processed:
                print(f"  Serializing to: {dataset_paths.processed}")
                serialize_email_data(email_data, path=dataset_paths.processed)

    print("\nEmail parsing and serialization complete.")
