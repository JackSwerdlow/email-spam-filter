"""General-purpose analysis utilities for data inspection and evaluation."""

from __future__ import annotations

import collections
import typing

import eli5
import matplotlib.pyplot as plt
import scipy
import scipy.special
import shap

from email_spam_filter.common import clean_html
from email_spam_filter.ml.common import to_features

if typing.TYPE_CHECKING:
    from email_spam_filter.common.containers import EmailData
    from email_spam_filter.ml.common import ModelPipeline


def get_model_features(model: ModelPipeline) -> collections.OrderedDict[str, float]:
    """Return all spam- and ham-indicative features of a trained model.

    Args:
        model: A trained ModelPipeline instance.

    Returns:
        An ordered dict mapping feature_names to weights, sorted from the
        largest positive (spam-indicative) weight down to the most negative (ham-indicative).
    """
    classifier_step = list(model.model.named_steps)[-1]
    feature_names = model.properties[classifier_step]["feature_names_out"].ravel()
    explanation = eli5.sklearn.explain_weights_sklearn(model.model, feature_names=feature_names)
    feature_weights = explanation.targets[0].feature_weights
    all_weights = feature_weights.pos + feature_weights.neg
    sorted_weights = sorted(all_weights, key=lambda w: w.weight, reverse=True)

    return collections.OrderedDict(
        (w.feature.replace(":", "__"), float(w.weight)) for w in sorted_weights
    )


def predicted_email_summary(email: EmailData, probability: float, *, max_chars: int = 500) -> str:
    """Return a formatted summary for a single predicted email.

    Args:
        email: An EmailData instance.
        probability: Model-predicted spam probability for the email.
        max_chars: Length of body snippet to include.

    Returns:
        A string giving a summary of the provided email.
    """
    snippet = clean_html(email.body)[:max_chars]

    return (
        f"ID:      {email.id}\n"
        f"Sender:  {email.from_addr}\n"
        f"Subject: {email.subject!r}\n"
        f"Score:   {probability:.3f}\n"
        f"Snippet: {snippet}"
    )


def show_email_features(
    model: ModelPipeline,
    email: EmailData,
    training_emails: list[EmailData],
    *,
    max_display: int = 20,
) -> None:
    """Waterfall plot of the top features for one e-mail prediction in log-odds.

    Args:
        model: A trained ModelPipeline instance.
        email: An EmailData instance.
        training_emails: Full EmailData training set. (labelled)
        max_display: How many of the top features to display
    """
    training_feature_df, _ = to_features(training_emails)
    email_feature_df, _ = to_features([email])

    preprocessor = model.model[:-1]
    classifier = model.model[-1]

    training_feature_array = preprocessor.transform(training_feature_df).toarray()
    email_feature_array = preprocessor.transform(email_feature_df).toarray()

    explainer = shap.LinearExplainer(classifier, training_feature_array)
    values = explainer.shap_values(email_feature_array)[0]
    base_value_logit = explainer.expected_value
    predicted_value_logit = base_value_logit + values.sum()

    explanation = shap.Explanation(
        values=values,
        base_values=base_value_logit,
        data=email_feature_array[0],
        feature_names=model.properties[list(model.model.named_steps)[-1]]["feature_names_out"],
    )

    shap.plots.waterfall(explanation, max_display=max_display, show=False)

    base_value_prob = scipy.special.expit(base_value_logit)
    predicted_value_prob = scipy.special.expit(predicted_value_logit)

    plt.title(f"P(spam): {predicted_value_prob:.1%}   (baseline {base_value_prob:.1%})")
    plt.show()
