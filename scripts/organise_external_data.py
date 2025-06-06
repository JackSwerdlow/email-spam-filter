"""Script to organise both the TREC Public Spam Corpus and SpamAssassin external datasets.

Before running:
    1. Ensure you have downloaded and unzipped the TREC dataset into:
       `data/raw_external/trec`
       ensuring that a `full/index` file and `data/` folder exists under that path.

    2. Ensure you have downloaded and unzipped the SpamAssassin public corpus into:
       `data/raw_external/spamassassin`
       with subfolders whose names include “ham” and “spam”.

    3. Install dev dependencies via Poetry (if not already done):
       > poetry install --with dev

Usage:
    > python organise_datasets.py

This will create (if missing) the following folders and move the .eml files into them:
    - `data/raw/trec_ham`
    - `data/raw/trec_spam`
    - `data/raw/spamassassin_ham`
    - `data/raw/spamassassin_spam`
"""

from __future__ import annotations

from email_spam_filter.common import logger
from email_spam_filter.data.organise import DATASET_MODULES

if __name__ == "__main__":
    logger()
    for organise_dataset in DATASET_MODULES.values():
        organise_dataset()
