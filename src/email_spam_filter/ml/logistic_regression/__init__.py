"""Logistic Regression Spam Classification Pipeline.

Binary linear classifier trained via maximum likelihood estimation.

This model estimates class membership probabilities using the logistic sigmoid
function applied to a weighted linear combination of input features. Parameters
are optimized by minimizing the negative log-likelihood under a Bernoulli distribution.

Modules:
    functions: Logistic regression functions for feature extraction, training, and prediction.
    model: Defines the logistic regression pipeline architecture.
"""

from __future__ import annotations

from email_spam_filter.ml.common.containers import ModelPipeline
from email_spam_filter.ml.logistic_regression.functions import prediction_model, training_model
from email_spam_filter.ml.logistic_regression.model import model


def logistic_regression_pipeline() -> ModelPipeline:
    """Factory for a new instance of the Logistic Regression pipeline."""
    return ModelPipeline(
        name="Logistic Regression",
        model=model,
        training_model=training_model,
        prediction_model=prediction_model,
    )
