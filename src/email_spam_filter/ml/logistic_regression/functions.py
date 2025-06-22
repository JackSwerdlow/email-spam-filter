"""Logistic regression functions for feature extraction, training, and prediction."""

from __future__ import annotations

import typing

import pandas as pd

if typing.TYPE_CHECKING:
    from logging import Logger

    from sklearn.pipeline import Pipeline

    from email_spam_filter.common.containers import EmailData, TagData


def to_features(emails: list[EmailData]) -> tuple[pd.DataFrame, pd.Series[int]]:
    """Convert a list of EmailData into feature DataFrame and label Series.

    Args:
        emails: list of EmailData objects.
    """
    records: list[dict[str, typing.Any]] = [
        {
            "id": email.id,
            "tag": email.tag,
            "source": email.source,
            "subject": email.subject,
            "body": email.body,
            "from_addr": email.from_addr,
            "n_links": email.n_links,
            "n_dupe_links": email.n_dupe_links,
            "n_rcpts": email.n_rcpts,
            "has_attach": email.has_attach,
            "auth_fail": email.auth_fail,
            "unique_html_tags": email.unique_html_tags,
        }
        for email in emails
    ]
    dataframe = pd.DataFrame.from_records(records)
    y = (dataframe["tag"] == "spam").astype(int)
    return dataframe, y


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
