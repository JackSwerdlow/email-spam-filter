"""Script to train a spam classification model on labelled emails and predict on inbox emails.

Before running:
    1. Ensure personal email data has already been parsed and serialised to:
       - data/processed/personal_processed.parquet

    2. Install dependencies via Poetry (if not already done):
       > poetry install

Usage:
    > python test_ml_model.py

This script will:
    - Load the processed personal email dataset
    - Split it into labelled (spam/ham) and unlabelled (inbox) subsets
    - Train a logistic regression model on the labelled data
    - Predict spam probabilities for each inbox email
    - Print the top 5 most spam- and ham-indicative features
    - Print the most confidently predicted spam and ham emails with a preview
"""

from __future__ import annotations

from email_spam_filter.common import clean_html, logger, paths
from email_spam_filter.data.io.functions import deserialize_email_data
from email_spam_filter.ml.common import split_labelled_and_inbox
from email_spam_filter.ml.models import MachineLearningModel

logger()

if paths.PERSONAL_PATHS.processed:
    emails = deserialize_email_data(paths.PERSONAL_PATHS.processed)
labelled, inbox = split_labelled_and_inbox(emails)

model = MachineLearningModel.LOGISTIC_REGRESSION.pipeline()
model.train(labelled)
results = model.predict(inbox)

feature_names = model.properties["classifier"]["feature_names_out"].ravel()
coefs = model.properties["classifier"]["coef_"].ravel()
feat_coef = list(zip(feature_names, coefs, strict=True))
top_spam = sorted(feat_coef, key=lambda x: x[1], reverse=True)[:5]
top_ham = sorted(feat_coef, key=lambda x: x[1])[:5]
print("\nTop 5 spam-indicative features:")
for feat, weight in top_spam:
    print(f"  {feat}: {weight:.3f}")
print("\nTop 5 ham-indicative features:")
for feat, weight in top_ham:
    print(f"  {feat}: {weight:.3f}")

most_spam_row = results.loc[results["probability"].idxmax()]
most_ham_row = results.loc[results["probability"].idxmin()]
most_spam_email = next(e for e in inbox if e.id == most_spam_row["id"])
most_ham_email = next(e for e in inbox if e.id == most_ham_row["id"])
print("\nMost likely SPAM:")
print(f"  ID:      {most_spam_email.id}")
print(f"  Subject: {most_spam_email.subject!r}")
print(f"  Score:   {most_spam_row['probability']:.3f}")
print("  Snippet:", clean_html(most_spam_email.body)[:500], "\n")
print("Most likely HAM:")
print(f"  ID:      {most_ham_email.id}")
print(f"  Subject: {most_ham_email.subject!r}")
print(f"  Score:   {most_ham_row['probability']:.3f}")
print("  Snippet:", clean_html(most_ham_email.body)[:500])
