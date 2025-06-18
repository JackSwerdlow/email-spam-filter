"""Script to interactively label personal inbox emails as spam, ham or inbox (unknown).

Before running:
    1. Install dev dependencies via Poetry (if not already done):
       > poetry install --with dev

    2. Ensure personal inbox emails have been fetched and parsed:
       - Run `fetch_imap_inbox.py` to download raw emails.
       - Run `parse_emails.py` to generate structured EmailData in Parquet format.

Usage:
    > python label_personal.py

This will open an interactive session to assign labels to each email.
Labels will be saved incrementally to:
    - data/labels/personal_labels.json
"""

from __future__ import annotations

from email_spam_filter.common import paths, simple_logger
from email_spam_filter.data.labelling import run_labelling_session

if __name__ == "__main__":
    simple_logger()
    run_labelling_session(paths.PERSONAL_PATHS.processed, paths.PERSONAL_PATHS.labels)
