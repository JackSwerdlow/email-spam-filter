"""Tests for functions for the machine learning Logistic Regression module."""

from __future__ import annotations

import typing

import numpy as np
import pandas as pd
import pytest

from email_spam_filter.common.containers import (
    AttributeData,
    EmailData,
    TagData,
    ValueData,
)
from email_spam_filter.ml.common import to_features
from email_spam_filter.ml.logistic_regression.functions import (
    extract_html_features,
    prediction_model,
    training_model,
)

if typing.TYPE_CHECKING:
    import pytest_mock


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
                count=2,
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
    return [_make_email(1, "spam"), _make_email(2, "ham")]


def test_extract_html_features(sample_emails_fixture: list[EmailData]) -> None:
    tag_lists = [e.unique_html_tags for e in sample_emails_fixture]
    features = extract_html_features(tag_lists)

    assert isinstance(features, list)
    assert len(features) == 2
    expected_keys = {
        "tag_p_count",
        "p_attr_style_count",
        "p_attr_style_value_color:red_count",
    }
    assert expected_keys.issubset(features[0].keys())
    assert features[0]["tag_p_count"] == 2


def test_training_model(
    sample_emails_fixture: list[EmailData],
    mocker: pytest_mock.MockerFixture,
) -> None:
    fake_pipe = mocker.MagicMock()
    fake_pipe.fit.return_value = fake_pipe

    logger = mocker.MagicMock()
    trained = training_model(fake_pipe, sample_emails_fixture, logger)
    fake_pipe.fit.assert_called_once()

    x, y = to_features(sample_emails_fixture)
    args, _ = fake_pipe.fit.call_args
    assert args[0].shape == x.shape
    assert np.array_equal(args[1], y.to_numpy())
    assert trained is fake_pipe


def test_prediction_model_returns_probs(
    sample_emails_fixture: list[EmailData],
    mocker: pytest_mock.MockerFixture,
) -> None:
    probs = np.array([[0.3, 0.7], [0.8, 0.2]])

    fake_pipe = mocker.MagicMock()
    fake_pipe.predict_proba.return_value = probs

    pred_df = prediction_model(sample_emails_fixture, fake_pipe)
    assert isinstance(pred_df, pd.DataFrame)
    assert list(pred_df["id"]) == [1, 2]
    assert np.allclose(pred_df["probability"].to_numpy(), probs[:, 1])
