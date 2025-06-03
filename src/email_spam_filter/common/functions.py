"""Generic utility functions."""

from __future__ import annotations

import typing

import yaml

from email_spam_filter.common.paths import CONFIG_PATH


def load_user_config() -> dict[str, typing.Any]:
    """Load user config from a YAML file."""
    if not CONFIG_PATH.exists():
        error_message = "Missing user_config.yml file."
        raise FileNotFoundError(error_message)
    with CONFIG_PATH.open() as file:
        user_config: dict[str, typing.Any] = yaml.safe_load(file)
        return user_config
