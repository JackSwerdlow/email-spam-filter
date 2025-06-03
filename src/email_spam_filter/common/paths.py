"""Paths to important project resources."""

from __future__ import annotations

from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[3]
"""Base directory of the project."""

CONFIG_PATH = BASE_DIR / "user_config.yml"
"""Path to the user config file."""

DATA_DIR = BASE_DIR / "data"
"""Path to the data folder."""

RAW_DIR = DATA_DIR / "raw"
"""Path to the raw data folder."""
