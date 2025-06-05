"""Shared dataclass definitions for structured data exchange across modules."""

from __future__ import annotations

import dataclasses
import typing

if typing.TYPE_CHECKING:
    import pathlib


@dataclasses.dataclass(frozen=True)
class DatasetPaths:
    """Holds all the Path objects for a given dataset.

    Attributes:
        external: Path to the external raw data download folder.
        raw_ham: Path to the raw folder where ham .eml files are stored.
        raw_spam: Path to the raw folder where spam .eml files are stored.
        raw_inbox: Path to the raw folder where inbox .eml files are stored.
        processed: Path to the processed Parquet database.
        labels: Path to the .json labels file.
    """

    raw_external: pathlib.Path | None
    raw_ham: pathlib.Path | None
    raw_spam: pathlib.Path | None
    raw_inbox: pathlib.Path | None
    processed: pathlib.Path | None
    labels: pathlib.Path | None
