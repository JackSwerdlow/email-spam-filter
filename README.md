# EmailSpamFilter

A personal learning project: building a machine‑learning‑powered spam filter for email.

## Overview

This is a personal project that uses machine learning to classify emails as spam or ham (real). It supports:

- Fetching and storing your own inbox data [Currently only from Virgin Media inboxes.]
---

## Quick‑Start Guide

```bash
# 1 Install miniconda
curl -L https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh \
  -o miniconda.sh && bash miniconda.sh -b -p $HOME/miniconda && rm miniconda.sh
eval "$($HOME/miniconda/bin/conda shell.zsh hook)"

#2 Configure conda channels to use conda-forge
conda config --add channels conda-forge
conda config --set channel_priority strict

#3 Install Poetry and conda-lock
conda install -y poetry conda-lock

#4 Install environment
conda-lock install -n email-spam-filter
conda activate email-spam-filter

#5 Install Poetry dependancies
poetry install

# 6 Install pre-commit hooks (If you plan on contributing)
poetry run pre-commit install
poetry run pre-commit install --hook-type pre-push
```

## Project layout

```
email-spam-filter/
├─ data/                              # Local data folders for project. Contents not uploaded to github.
│   ├─ labels/                        # Contains label files.
│   ├─ processed/                     # Processed emails.
│   ├─ raw/                           # Raw .eml files.
│   └─ raw_external/                  # Raw unformatted external databases (e.g TREC Public Copora)
├─ scripts/                           # Example scripts to show functionality.
│   └─ fetch_inbox.py/                # Script that fetches emails as .eml files from an inbox using IMAP.
├─ src/
│   └─ email_spam_filter/             # The email_spam_filter package.
│       ├─ __init__.py
│       ├─ common/                    # Module with common utilities and classes used in other modules.
│       │   ├─ __init__.py
│       │   ├─ constants.py
│       │   ├─ functions.py
│       │   └─ paths.py
│       └─ data/                      # Module for data handling.
│           ├─ __init__.py
│           └─ collection/
│               ├─ __init__.py
│               └─ personal/
│                   ├─ __init__.py
│                   └─ functions.py
│
├─ tests/                             # Unit tests
├─ .gitignore
├─ conda-lock.yml
├─ environment.yml
├─ poetry.lock
├─ pyproject.toml
├─ README.md
└─ user_config.yml                    # User config file to allow for gathering personal email data.
```
## Configuration

Project behaviour can be customized in `user_config.yml`:

```yaml
user_email: "your_username@example.com"
imap_host: "imap.virginmedia.com"
keyring_service: "virgin-imap"
folder_map:
  INBOX: inbox
  Spam: spam
```

## Running Example Scripts

```bash
# Ensure you are in the email-spam-filter conda environment
conda activate email-spam-filter
poetry install

#1 Edit the user_config.yml file to ensure details are correct.
#Then run the following, replacing with your own email and password when prompted.
#This will be encrypted at ~/.local/share/python_keyring/ , no plain text passwords don't worry!
python -m keyring set virgin-imap your_username@virginmedia.com

#2 Fetch your inbox
poetry run python scripts/fetch_imap_inbox.py
```
