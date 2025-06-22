"""Currently existing machine learning models."""

from __future__ import annotations

import enum
import typing

from email_spam_filter.ml.logistic_regression import logistic_regression_pipeline

if typing.TYPE_CHECKING:
    from email_spam_filter.ml.common import ModelPipeline


class MachineLearningModel(enum.Enum):
    """Currently existing machine learning models."""

    LOGISTIC_REGRESSION = enum.auto()

    def pipeline(self) -> ModelPipeline:
        """Returns the models pipeline."""
        return MODEL_PIPELINES[self]()


MODEL_PIPELINES = {
    MachineLearningModel.LOGISTIC_REGRESSION: logistic_regression_pipeline,
}
