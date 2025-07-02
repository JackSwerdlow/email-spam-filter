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
    - Print the top 5 most spam- and ham-indicative features (raw weights)
    - Print the most confidently predicted spam and ham emails with a preview
    - Display the main features that contributed to the models decision on the most confidently
      predicted spam and ham emails (SHAP).
"""

from __future__ import annotations

from email_spam_filter.analysis import (
    get_model_features,
    predicted_email_summary,
    show_email_features,
)
from email_spam_filter.common import email_by_id, logger, paths
from email_spam_filter.data.io.functions import deserialize_email_data
from email_spam_filter.ml.common import split_labelled_and_inbox
from email_spam_filter.ml.models import MachineLearningModel

logger()

if paths.PERSONAL_PATHS.processed:
    emails = deserialize_email_data(paths.PERSONAL_PATHS.processed)
labelled, inbox = split_labelled_and_inbox(emails)

model = MachineLearningModel.LOGISTIC_REGRESSION.pipeline()
model.train(labelled)

model_features = get_model_features(model)
print("\nTop 5 spam-indicative features:")
for feat, w in list(model_features.items())[:5]:
    print(f"  {feat}: {w:.3f}")
print("\nTop 5 ham-indicative features:")
for feat, w in reversed(list(model_features.items())[-5:]):
    print(f"  {feat}: {w:.3f}")

results = model.predict(inbox)
ranked_results = results.sort_values(by=["probability", "id"], ascending=[False, True])

most_likely_spam_row = ranked_results.iloc[0]
most_likely_spam_email = email_by_id(int(ranked_results.iloc[0]["id"]), inbox)

most_likely_ham_row = ranked_results.iloc[-1]
most_likely_ham_email = email_by_id(int(ranked_results.iloc[-1]["id"]), inbox)

print("\nMost likely SPAM:")
print(predicted_email_summary(most_likely_spam_email, most_likely_spam_row["probability"]))
show_email_features(model, most_likely_spam_email, labelled, max_display=20)

print("\nMost likely HAM:")
print(predicted_email_summary(most_likely_ham_email, most_likely_ham_row["probability"]))
show_email_features(model, most_likely_ham_email, labelled, max_display=20)
