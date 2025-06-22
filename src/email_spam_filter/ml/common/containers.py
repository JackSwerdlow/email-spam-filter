"""Model pipeline containers."""

from __future__ import annotations

import logging
import typing

if typing.TYPE_CHECKING:
    import pandas as pd
    from sklearn.pipeline import Pipeline

    from email_spam_filter.common.containers import EmailData


class ModelPipeline:
    """Generic model pipeline wrapper for training and prediction."""

    def __init__(
        self,
        name: str,
        model: typing.Callable[[], Pipeline],
        training_model: typing.Callable[[Pipeline, list[EmailData], logging.Logger], Pipeline],
        prediction_model: typing.Callable[[list[EmailData], Pipeline], pd.DataFrame],
    ) -> None:
        """Initialize a ModelPipeline instance.

        Args:
            name: A human-readable name for the model.
            model: A function that constructs and returns an untrained pipeline.
            training_model: A function that accepts EmailData, a logger and a pipeline to train.
            prediction_model: A function that performs prediction using the trained pipeline.
        """
        self.name = name
        self._model = model
        self._train = training_model
        self._is_trained = False
        self._predict = prediction_model
        self.model: Pipeline = self._model()

    @property
    def properties(self) -> dict[str, typing.Any]:
        """Return all learned attributes and structure of each pipeline step."""
        if not self._is_trained:
            error_message = "Model has not been trained yet. Call `train()` first."
            raise RuntimeError(error_message)
        props = {name: vars(step) for name, step in self.model.named_steps.items()}
        try:
            feature_names = self.model[:-1].get_feature_names_out()
        except Exception as error:
            error_message = f"Unable to get feature names from preprocessor: {error}"
            raise RuntimeError(error_message) from error
        classifier_name = list(self.model.named_steps)[-1]
        props[classifier_name]["feature_names_out"] = feature_names
        return props

    def train(self, emails: list[EmailData]) -> ModelPipeline:
        """Train the model and store the fitted pipeline."""
        logger = logging.getLogger(__name__)
        self.model = self._train(self.model, emails, logger)
        self._is_trained = True
        return self

    def predict(self, emails: list[EmailData]) -> pd.DataFrame:
        """Run prediction on a list of emails using the trained model."""
        if not self._is_trained:
            error_message = "Model has not been trained yet. Call `train()` first."
            raise RuntimeError(error_message)
        return self._predict(emails, self.model)

    def summary(self) -> None:
        """Log a summary of the pipeline steps."""
        logger = logging.getLogger(__name__)
        logger.info("[ModelPipeline: %s] Pipeline summary:\n%s", self.name, self.model)
