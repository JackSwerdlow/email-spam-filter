"""Generic utility functions."""

from __future__ import annotations

import functools
import logging

import pydantic

from email_spam_filter.common.containers import UserConfig


def logger(level: int = logging.INFO) -> None:
    """Configure root logger with the specified level.

    Args:
        level: Logging level (Default: logging.INFO)
    """
    logging.basicConfig(
        level=level,
        format="%(asctime)s %(levelname)-8s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )


def simple_logger(level: int = logging.INFO) -> None:
    """Configure a simple root logger with the specified level.

    Args:
        level: Logging level (Default: logging.INFO)
    """
    logging.basicConfig(
        level=level,
        format="%(message)s",
    )


@functools.lru_cache
def load_user_config() -> UserConfig:
    """Load user config from a .env file."""
    try:
        return UserConfig()
    except pydantic.ValidationError as exception:
        missing = ", ".join(str(error["loc"][0]) for error in exception.errors())
        error_message = (
            f"Missing configuration values: {missing}. "
            "Run `poetry run setup` then edit the created `.env` file."
        )
        raise RuntimeError(error_message) from exception
