"""General-purpose pre-processing, evaluation, and data management routines."""

from __future__ import annotations

import logging
import typing

import pandas as pd

if typing.TYPE_CHECKING:
    from email_spam_filter.common.containers import EmailData

logger = logging.getLogger(__name__)


def to_features(emails: list[EmailData]) -> tuple[pd.DataFrame, pd.Series[int]]:
    """Convert a list of EmailData into feature DataFrame and label Series.

    Args:
        emails: A list of EmailData instances.

    Returns:
        A tuple with the created feature dataframe and label series. (X, y)
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
    labels = (dataframe["tag"] == "spam").astype(int)
    return dataframe, labels


def split_labelled_and_inbox(emails: list[EmailData]) -> tuple[list[EmailData], list[EmailData]]:
    """Split emails into labelled (spam/ham) and unlabelled (inbox) subsets.

    Args:
        emails: List of EmailData instances.

    Returns:
        A tuple containing:
        - List of emails labelled as 'spam' or 'ham'.
        - List of emails labelled as 'inbox'.
    """
    labelled = [e for e in emails if e.tag in ("spam", "ham")]
    n_spam = sum(1 for e in labelled if e.tag == "spam")
    n_ham = sum(1 for e in labelled if e.tag == "ham")
    logger.info("Labelled dataset: %d spam, %d ham (total %d)", n_spam, n_ham, len(labelled))
    inbox = [e for e in emails if e.tag == "inbox"]
    logger.info("Inbox emails: %d", len(inbox))
    return labelled, inbox
