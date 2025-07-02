"""Logistic regression functions for feature extraction, training, and prediction."""

from __future__ import annotations

import typing

import pandas as pd

from email_spam_filter.ml.common import to_features

if typing.TYPE_CHECKING:
    from logging import Logger

    from sklearn.pipeline import Pipeline

    from email_spam_filter.common.containers import EmailData, TagData


def training_model(model: Pipeline, emails: list[EmailData], logger: Logger) -> Pipeline:
    """Train the provided scikit-learn pipeline on the labelled email data."""
    x, y = to_features(emails)
    logger.info("Training logistic regression model on %d samples.", len(emails))
    return model.fit(x, y)


def prediction_model(emails: list[EmailData], model: Pipeline) -> pd.DataFrame:
    """Run prediction on email data and return spam probabilities."""
    x, _ = to_features(emails)
    probabilities = model.predict_proba(x)[:, 1]
    return pd.DataFrame({"id": [e.id for e in emails], "probability": probabilities})


def extract_html_features(html_series: list[tuple[TagData, ...]]) -> list[dict[str, int]]:
    """Convert list of HTML tag tuples into count feature dictionaries."""
    feature_dicts = []
    for tags in html_series:
        feats = {}
        for tag in tags:
            feats[f"tag_{tag.tag}_count"] = tag.count
            for attribute in tag.attributes:
                a = attribute.attribute
                feats[f"{tag.tag}_attr_{a}_count"] = attribute.count
                for value in attribute.values:  # noqa: PD011
                    feats[f"{tag.tag}_attr_{a}_value_{value.value}_count"] = value.count
        feature_dicts.append(feats)
    return feature_dicts
