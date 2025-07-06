# EmailSpamFilter

A personal learning project: building a machine‑learning‑powered spam filter for email.

## Overview

This is a personal project that uses machine learning to classify emails as spam or ham (real). It supports:

- Fetching and storing your own inbox data [Currently only tested on Virgin Media inboxes.]
- Labelling emails with tags (spam, ham, inbox)
- Organizing public datasets (TREC, SpamAssassin) [Currently datasets must be downloaded by user
  manually.]
- Training a logistic regression model on email features [Other models are WIP]
- Evaluating and inspecting model performance.

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

#6 Setup default `.env` file with poetry
poetry run setup

# 7 Install pre-commit hooks (If you plan on contributing)
poetry run pre-commit install
poetry run pre-commit install --hook-type pre-push
```

## Project layout

```
email-spam-filter/
├─ data/                              # Local data folders for project. Contents not uploaded to github.
│   ├─ labels/                        # Contains JSON files with ham, spam, inbox labels for datasets.
│   ├─ processed/                     # Processed emails stored as EmailData objects in Parquet databases.
│   ├─ raw/                           # Raw .eml files.
│   └─ raw_external/                  # Raw unformatted external databases (e.g TREC Public Copora)
├─ scripts/                           # Example scripts to show functionality.
│   ├─ fetch_imap_inbox.py            # Script to download personal emails via IMAP and save them to disk.
│   ├─ label_inbox.py                 # Script to interactively label personal inbox emails as spam, ham or inbox (unknown).
│   ├─ organise_external_data.py      # Script to organise external datasets.
│   ├─ parse_emails.py                # Script to parse raw .eml files from all datasets and serialize them.
│   └─ test_ml_model.py               # Script to train a classification model on labelled emails and predict on other emails.
├─ src/
│   └─ email_spam_filter/             # The email_spam_filter package.
│       ├─ __init__.py
│       ├─ analysis/                  # Module for data, email and results analysis and visualisation.
│       │   ├─ __init__.py
│       │   └─ functions.py
│       ├─ common/                    # Module with common utilities, classes and paths used in other modules.
│       │   ├─ __init__.py
│       │   ├─ constants.py
│       │   ├─ containers.py
│       │   ├─ functions.py
│       │   └─ paths.py
│       ├─ data/                      # Module specifically for data collection, processing, organising and labelling.
│       │   ├─ __init__.py
│       │   ├─ collection/
│       │   │   ├─ __init__.py
│       │   │   └─ personal/
│       │   │       ├─ __init__.py
│       │   │       └─ functions.py
│       │   ├─ io/
│       │   │   ├─ __init__.py
│       │   │   └─ functions.py
│       │   ├─ labelling/
│       │   │   ├─ __init__.py
│       │   │   └─ functions.py
│       │   └─ organise/
│       │       ├─ __init__.py
│       │       ├─ spamassassin/
│       │       │   ├─ __init__.py
│       │       │   └─ functions.py
│       │       └─ trec/
│       │           ├─ __init__.py
│       │           └─ functions.py
│       └─ ml/                        # Module containing all machine learning components.
│           ├─ __init__.py
│           ├─ common
│           │   ├─ __init__.py
│           │   ├─ containers.py
│           │   └─ functions.py
│           ├─ logistic_regression
│           │   ├─ __init__.py
│           │   ├─ functions.py
│           │   └─ model.py
│           └─ models.py
├─ tests/                             # Unit tests
├─ .gitignore
├─ .pre-commit-config.yaml
├─ conda-lock.yml
├─ environment.yml
├─ poetry.lock
├─ pyproject.toml
├─ LICENSE
├─ README.md
└─ .env                               # User config file to allow for gathering personal email data.
```
## Configuration

Project behaviour can be customized in `.env` file that is created if `poetry run setup` was
correctly run:

```
USER_EMAIL='your_username@example.com'
IMAP_HOST='imap.virginmedia.com'
KEYRING_SERVICE='virgin-imap'
FOLDER_MAP='{"INBOX": "inbox", "Spam": "spam"}'
```
| Variable              | Purpose                                                                                                                      |
| --------------------- | ---------------------------------------------------------------------------------------------------------------------------- |
| **`USER_EMAIL`**      | Email address used to log in to the IMAP server.                                                                             |
| **`IMAP_HOST`**       | Hostname of your email provider’s IMAP server.                                                                               |
| **`KEYRING_SERVICE`** | Service key under which the IMAP password is stored in your OS keyring.                                                      |
| **`FOLDER_MAP`**      | JSON mapping of IMAP folder names to short, local labels (add or modify as needed - for example: `{... , "Trash":"trash"}`). |


## Running Example Scripts

```bash
# Ensure you are in the email-spam-filter conda environment
conda activate email-spam-filter
poetry install

#1 Edit the .env file to ensure details are correct.
#Then run the following, replacing with your own email and password when prompted.
#This will be encrypted at ~/.local/share/python_keyring/ , no plain text passwords don't worry!
python -m keyring set virgin-imap your_username@virginmedia.com

#2.1 Fetch your inbox
poetry run python scripts/fetch_imap_inbox.py

#(OPTIONAL)
#3.1 Download and unzip the following datasets into the data/raw_external folder.
# TREC Public Corpus https://plg.uwaterloo.ca/cgi-bin/cgiwrap/gvcormac/foo
# SpamAssassin Public Corpus https://spamassassin.apache.org/old/publiccorpus/
#Ensure they are stored and named like data/raw_external/trec, data/raw_external/spamassassin, etc.

#(OPTIONAL)
#3.2 Organise the external databases into a parsable format.
poetry run python scripts/organise_external_data.py

#4.1 Parse all raw .eml files into EmailData objects and write them to Parquet databases.
poetry run python scripts/parse_emails.py

#(OPTIONAL)
#4.2 Label the personal inbox emails as spam, ham or inbox (unknown). Inbox is the default label if not manually labelled.
poetry run python scripts/label_inbox.py

#5 Train a simple Logistic Regression model on labelled personal email data and then predict for unlabelled emails.
## This will only work if step 4.2 was performed. However if wanting to use external data to train and predict on, the path can be edited to use a different dataset.
poetry run python scripts/test_ml_model.py
```
The accuracy of the model is determined by how large the training dataset is and how varied the real
and spam emails given are.


## Datasets Used

- [SpamAssassin Public Corpus](https://spamassassin.apache.org/old/publiccorpus/)
- [TREC Public Email Dataset](https://plg.uwaterloo.ca/cgi-bin/cgiwrap/gvcormac/foo)
