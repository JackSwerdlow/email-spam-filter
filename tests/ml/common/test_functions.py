"""Tests for functions for the machine learning common module."""

from __future__ import annotations

import pandas as pd
import pytest

from email_spam_filter.common.containers import (
    AttributeData,
    EmailData,
    TagData,
    ValueData,
)
from email_spam_filter.ml.common import split_labelled_and_inbox, to_features


def _make_email(
    idx: int,
    tag: str,
    subject: str = "hello",
    n_links: int = 0,
) -> EmailData:
    return EmailData(
        id=idx,
        tag=tag,
        source="test",
        subject=subject,
        body="Plain text",
        unique_html_tags=(
            TagData(
                tag="p",
                count=1,
                attributes=(
                    AttributeData(
                        attribute="style",
                        count=1,
                        values=(ValueData(value="color:red", count=1),),
                    ),
                ),
            ),
        ),
        from_addr="example@example.com",
        from_name="Tester",
        n_links=n_links,
        n_dupe_links=0,
        link_domains=(),
        link_contexts=(),
        n_rcpts=1,
        has_attach=False,
        auth_fail=False,
    )


@pytest.fixture
def sample_emails_fixture() -> list[EmailData]:
    return [
        _make_email(1, "spam", n_links=3),
        _make_email(2, "spam", n_links=1),
        _make_email(3, "spam"),
        _make_email(4, "ham"),
        _make_email(5, "ham"),
        _make_email(6, "inbox"),
    ]


def test_split_labelled_and_inbox(sample_emails_fixture: list[EmailData]) -> None:
    labelled, inbox = split_labelled_and_inbox(sample_emails_fixture)

    assert len(labelled) == 5
    assert len(inbox) == 1

    assert {e.tag for e in labelled} == {"spam", "ham"}
    assert len([e.tag for e in labelled if e.tag == "spam"]) == 3
    assert len([e.tag for e in labelled if e.tag == "ham"]) == 2
    assert inbox[0].tag == "inbox"
    assert isinstance(inbox[0], EmailData)


def test_to_features(sample_emails_fixture: list[EmailData]) -> None:
    df, labels = to_features(sample_emails_fixture)

    assert isinstance(df, pd.DataFrame)
    assert df.shape[0] == len(sample_emails_fixture)
    assert set(labels.unique()) == {0, 1}
    assert labels.sum() == 3

    expected_cols = {
        "id",
        "tag",
        "source",
        "subject",
        "body",
        "from_addr",
        "n_links",
        "n_dupe_links",
        "n_rcpts",
        "has_attach",
        "auth_fail",
        "unique_html_tags",
    }
    assert expected_cols.issubset(set(df.columns))
