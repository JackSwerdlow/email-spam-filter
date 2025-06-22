"""General-purpose pre-processing, evaluation, and data management routines."""

from __future__ import annotations

import logging
import typing

if typing.TYPE_CHECKING:
    from email_spam_filter.common.containers import EmailData

logger = logging.getLogger(__name__)


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
