"""Shared dataclass definitions for structured data exchange across modules."""

from __future__ import annotations

import dataclasses
import typing

import pydantic
import pydantic_settings

if typing.TYPE_CHECKING:
    import pathlib


class UserConfig(pydantic_settings.BaseSettings):
    """Configuration loaded from the environment or a .env file.

    Attributes:
        user_email: Email address used to log in to the IMAP server.
        imap_host: IMAP server host for the email provider.
        keyring_service: Service name used by keyring for password retrieval.
        folder_map: Mapping of IMAP folder names to short local labels.
    """

    user_email: str
    imap_host: str
    keyring_service: str
    folder_map: dict[str, str]

    model_config = pydantic_settings.SettingsConfigDict(frozen=True, env_file=".env")


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

    external: pathlib.Path | None
    raw_ham: pathlib.Path | None
    raw_spam: pathlib.Path | None
    raw_inbox: pathlib.Path | None
    processed: pathlib.Path | None
    labels: pathlib.Path | None


class FrozenBaseModel(pydantic.BaseModel):
    """Pydantic BaseModel configured to be immutable."""

    model_config = pydantic.ConfigDict(frozen=True)


class ValueData(FrozenBaseModel):
    """Represents a single HTML attribute value and how often it appears.

    Attributes:
        value: The attribute value (e.g., 'demo' from id="demo").
        count: Number of times this exact value was observed across all attributes and tags of a
               given name.
    """

    value: str
    count: int


class AttributeData(FrozenBaseModel):
    """Holds data for one HTML attribute across all tags of a given name.

    Attributes:
        attribute: The type of attribute (e.g., 'id', 'style', 'href').
        count: Total number of times this attribute appeared on that tag.
        values: A tuple of ValueData instances, one per unique attribute value on the attribute.
    """

    attribute: str
    count: int
    values: tuple[ValueData, ...]


class TagData(FrozenBaseModel):
    """Aggregates counts and attribute details for a single HTML tag type.

    Attributes:
        tag: The type of tag (e.g., 'div', 'a', 'p').
        count: How many times this tag appeared in a specific HTML.
        attributes: A tuple of AttributeData, one for each distinct attribute on the tag.
    """

    tag: str
    count: int
    attributes: tuple[AttributeData, ...]


class EmailData(FrozenBaseModel):
    """Container for parsed email information used for AI training.

    Attributes:
        id: Unique identifier of the email.
        tag: Type of email (e.g. spam, ham, inbox).
        source: Source of the email. (e.g. Personal, TREC, SpamAssassin).
        subject: Subject header of the email.
        body: Plain-text body of the email.
        unique_html_tags: TagData for each unique HTML tag in the message.
        from_addr: Sender email address.
        from_name: Sender display name.
        n_links: Total number of links found.
        n_dupe_links: Number of duplicate links.
        link_domains: Set of unique link domains.
        link_contexts: Tuple of HTML anchor snippets or URL context strings.
        n_rcpts: Number of recipients.
        has_attach: True if the email has attachments.
        auth_fail: True if authentication headers indicate failure.
    """

    id: int
    tag: str
    source: str
    subject: str
    body: str
    unique_html_tags: tuple[TagData, ...]
    from_addr: str
    from_name: str
    n_links: int
    n_dupe_links: int
    link_domains: tuple[str, ...]
    link_contexts: tuple[str, ...]
    n_rcpts: int
    has_attach: bool
    auth_fail: bool
