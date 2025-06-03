# EmailSpamFilter

A personal learning project: building a machine‑learning‑powered spam filter for email.

## Overview

This is a personal project that uses machine learning to classify emails as spam or ham (real).

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
poetry install --with=dev

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
├─ src/
│   └─ email_spam_filter/             # The email_spam_filter package.
│       └─ __init__.py
├─ tests/                             # Unit tests [WIP]
│   └─ __init__.py
├─ .gitignore
├─ conda-lock.yml
├─ environment.yml
├─ poetry.lock
├─ pyproject.toml
└─ README.md
```
