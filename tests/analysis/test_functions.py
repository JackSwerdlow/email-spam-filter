"""Tests for functions for the analysis module."""

from __future__ import annotations

import pytest

from email_spam_filter.analysis.functions import predicted_email_summary
from email_spam_filter.common.containers import EmailData, TagData


@pytest.fixture
def email_fixture() -> EmailData:
    return EmailData(
        id=42,
        tag="inbox",
        source="test",
        subject="Hello World",
        body="<p>This is <b>bold</b> text that should be cleaned. This should be cut off.</p>",
        from_addr="example@example.com",
        from_name="Example",
        n_links=0,
        n_dupe_links=0,
        link_domains=(),
        link_contexts=(),
        n_rcpts=1,
        has_attach=False,
        auth_fail=False,
        unique_html_tags=(TagData(tag="p", count=1, attributes=()),),
    )


def test_predicted_email_summary(email_fixture: EmailData) -> None:
    summary = predicted_email_summary(email_fixture, probability=0.6789, max_chars=41)

    assert "ID:      42" in summary
    assert "example@example.com" in summary
    assert "Hello World" in summary
    assert "Score:   0.679" in summary
    assert "Snippet:" in summary
    snippet_line = next(line for line in summary.splitlines() if line.startswith("Snippet:"))
    assert snippet_line.endswith("This is bold text that should be cleaned.")
