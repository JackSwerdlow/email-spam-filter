"""Common utilities and shared data structures for model development and evaluation.

Modules:
    containers: Model pipeline containers.
    functions: General-purpose pre-processing, evaluation, and data management routines.
"""

from __future__ import annotations

__all__ = (
    "ModelPipeline",
    "split_labelled_and_inbox",
)

from email_spam_filter.ml.common.containers import (
    ModelPipeline,
)
from email_spam_filter.ml.common.functions import (
    split_labelled_and_inbox,
)
