"""Generic utility functions."""

from __future__ import annotations

import functools
import logging
import quopri
import re

import pydantic
from bs4 import BeautifulSoup

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


def clean_html(html: str) -> str:
    """Decode and clean HTML content to extract meaningful plain-text.

    Args:
        html: Raw HTML content as a string.

    Returns:
        A cleaned, whitespace-normalized plain-text string.
    """
    logger = logging.getLogger(__name__)
    try:
        html = quopri.decodestring(html.encode("utf-8")).decode("utf-8", errors="ignore")
        soup = BeautifulSoup(html, "lxml")
        text = soup.get_text(separator="\n")
        lines = text.splitlines()
        cleaned = []
        for line in lines:
            cleaned_line = re.sub(r"[\u200b\u200c\u200d\u2060\uFEFF]", "", line)
            cleaned_line = cleaned_line.strip()
            if cleaned_line:
                cleaned.append(cleaned_line)
        return " ".join(cleaned)
    except (TypeError, UnicodeDecodeError) as error:
        logger.warning("Encountered error trying to clean HTML content, see DEBUG for details.")
        logger.debug(error)
        return html
