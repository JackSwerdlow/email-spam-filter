"""Utilities for reading, writing, and processing email-related data."""

from __future__ import annotations

__all__ = ()

import email
import email.policy
import email.utils
import json
import logging
import pathlib
import re
import typing
import urllib.parse

import bs4
import pandas as pd

from email_spam_filter.common.containers import (
    AttributeData,
    EmailData,
    TagData,
    ValueData,
)

if typing.TYPE_CHECKING:
    from email.message import EmailMessage

RAW_DIR: typing.Final[pathlib.Path] = pathlib.Path("data/raw")
logger = logging.getLogger(__name__)


def create_email_data(path: pathlib.Path) -> EmailData:
    """Read an .eml file from disk and return its parsed EmailData.

    Args:
        path: Filesystem path to the .eml file.

    Returns:
        An EmailData instance with all extracted fields.
    """
    with path.open("rb") as f:
        email_message = email.message_from_binary_file(f, policy=email.policy.default)
    folder = (path.parent).name
    uid = path.stem
    return parse_email_message(email_message, uid, folder)


def parse_email_message(email_message: EmailMessage, uid: str, folder_label: str) -> EmailData:
    """Extract EmailData from an EmailMessage object.

    Args:
        email_message: The EmailMessage object to parse.
        uid: Unique identifier to assign. Must be in form 123_tag. (e.g. 12_spam).
        folder_label: Folder label (e.g., 'inbox').

    Returns:
        An EmailData instance with parsed content.
    """
    id_str, tag = uid.split("_", 1)
    subject = email_message.get("Subject", "")

    try:
        raw_from = email_message.get("From", "")
    except ValueError as error:
        logger.info("MALFORMED 'From' HEADER in %s: ", f"{RAW_DIR}/{folder_label}/{uid}.eml")
        logger.debug(error)
        raw_from = ""
    from_name, from_addr = email.utils.parseaddr(raw_from)

    # workaround to avoid using '.get_all()' due to known bug, tracked in cpython#83281
    to_headers = []
    cc_headers = []
    for k, v in email_message.raw_items():
        if k.lower() == "to":
            to_headers.append(v)
        elif k.lower() == "cc":
            cc_headers.append(v)
    rcpt_headers = to_headers + cc_headers
    n_rcpts = len(email.utils.getaddresses(rcpt_headers))

    has_attach = any(
        part.get_content_disposition() == "attachment" for part in email_message.iter_attachments()
    )
    auth_fail = any(
        "fail" in hdr.lower() for hdr in email_message.get_all("Authentication-Results", [])
    )

    plain_body, html_body = _extract_email_parts(email_message, uid, folder_label)
    tag_counts = _extract_unique_tag_data(html_body)

    link_urls, contexts = _extract_link_contexts(plain_body, html_body)
    n_links = len(link_urls)
    n_dupe_links = n_links - len(set(link_urls))
    link_domains_set = set()
    for url in link_urls:
        try:
            netloc = urllib.parse.urlparse(url).netloc
            link_domains_set.add(netloc)
        except ValueError as error:
            logger.info("MALFORMED URL found in %s: %s", f"{RAW_DIR}/{folder_label}/{uid}.eml", url)
            logger.debug(error)
            link_domains_set.add("MALFORMED")
    link_domains = tuple(link_domains_set)

    return EmailData(
        id=int(id_str),
        tag=tag,
        source=folder_label.split("_", 1)[0],
        subject=subject,
        body=plain_body,
        unique_html_tags=tag_counts,
        from_addr=from_addr,
        from_name=from_name,
        n_links=n_links,
        n_dupe_links=n_dupe_links,
        link_domains=link_domains,
        link_contexts=contexts,
        n_rcpts=n_rcpts,
        has_attach=has_attach,
        auth_fail=auth_fail,
    )


def _extract_email_parts(
    email_message: EmailMessage, uid: str, folder_label: str
) -> tuple[str, str]:
    """Extract plain-text and HTML parts from the EmailMessage.

    Args:
        email_message: The EmailMessage object to inspect.
        uid: Unique identifier to assign. Must be in form 123_tag. (e.g. 12_spam).
        folder_label: Folder label (e.g., 'inbox').

    Returns:
        A tuple containing the plain-text and html parts of the EmailMessage.
    """
    if hasattr(email_message, "is_multipart") and email_message.is_multipart():
        return _extract_parts_multipart(email_message, uid, folder_label)
    return _extract_parts_nonmultipart(email_message, uid, folder_label)


def _extract_parts_multipart(
    email_message: EmailMessage, uid: str, folder_label: str
) -> tuple[str, str]:
    """Extract plain-text and HTML parts from a multipart EmailMessage.

    Args:
        email_message: The EmailMessage object to inspect.
        uid: Unique identifier to assign. Must be in form 123_tag. (e.g. 12_spam).
        folder_label: Folder label (e.g., 'inbox').

    Returns:
        A tuple containing the plain-text and html parts of the EmailMessage.
    """
    plain_body = ""
    html_body = ""
    for part in email_message.walk():
        if part.get_content_maintype() == "multipart":
            continue
        ctype = part.get_content_type()
        try:
            content = _safe_get_content(part, uid, folder_label)
        except KeyError:
            continue
        if isinstance(content, str):
            content = content.strip()
        else:
            continue
        if ctype == "text/plain" and not plain_body:
            plain_body = content
        elif ctype == "text/html" and not html_body:
            html_body = content
    return plain_body, html_body


def _extract_parts_nonmultipart(
    email_message: EmailMessage, uid: str, folder_label: str
) -> tuple[str, str]:
    """Extract plain-text and HTML parts from a non-multipart EmailMessage.

    Args:
        email_message: The EmailMessage object to inspect.
        uid: Unique identifier to assign. Must be in form 123_tag. (e.g. 12_spam).
        folder_label: Folder label (e.g., 'inbox').

    Returns:
        A tuple containing the plain-text and html parts of the EmailMessage.
    """
    plain_body = ""
    html_body = ""
    payload = email_message.get_payload()
    if isinstance(payload, str) and payload.strip():
        content = payload.strip()
        if email_message.get_content_type() == "text/plain":
            plain_body = content
        elif email_message.get_content_type() == "text/html":
            html_body = content
    else:
        try:
            content = _safe_get_content(email_message, uid, folder_label)
        except KeyError:
            return plain_body, html_body
        if isinstance(content, str):
            content = content.strip()
            if email_message.get_content_type() == "text/plain":
                plain_body = content
            elif email_message.get_content_type() == "text/html":
                html_body = content
    return plain_body, html_body


def _safe_get_content(email_message: EmailMessage, uid: str, folder_label: str) -> str:
    """Extract and decode the content from an email, swapping to an alternate decoder if needed.

    Args:
        email_message: The EmailMessage object to inspect.
        uid: Unique identifier to assign. Must be in form 123_tag. (e.g. 12_spam).
        folder_label: Folder label (e.g., 'inbox').

    Returns:
        Decoded string content of the email_message or, if decoding fails, returns an empty string.
    """
    try:
        content = email_message.get_content()
        if isinstance(content, str):
            return content
    except LookupError as error:
        payload = email_message.get_payload(decode=True)
        if isinstance(payload, bytes):
            logger.info(
                "Unknown email encoding found in %s; using utf-8 fallback.",
                f"{RAW_DIR}/{folder_label}/{uid}.eml",
            )
            logger.debug(error)
            return payload.decode("utf-8", errors="replace")
        logger.warning("[!] No payload for email part in %s: %s", uid, error)

    return ""


def _extract_unique_tag_data(html_body: str) -> tuple[TagData, ...]:
    """Extract TagData describing each unique tag in the HTML.

    Args:
        html_body: The email's HTML body.

    Returns:
        A list containing TagData for each unique tag in the HTML.
    """
    unique_html_tags: list[TagData] = []
    tag_dict: dict[str, dict[str, typing.Any]] = {}

    try:
        soup = bs4.BeautifulSoup(html_body, "html.parser")
    except bs4.exceptions.ParserRejectedMarkup:
        soup = bs4.BeautifulSoup(html_body, "html5lib")
    for tag in soup.find_all():
        if not isinstance(tag, bs4.Tag):
            continue
        entry = tag_dict.setdefault(tag.name, {"count": 0, "attributes": {}})
        entry["count"] += 1
        for attr, val in tag.attrs.items():
            attr_entry = entry["attributes"].setdefault(attr, {"count": 0, "values": {}})
            attr_entry["count"] += 1
            values = val if isinstance(val, (list | tuple)) else [val]
            for value in values:
                attr_entry["values"][value] = attr_entry["values"].get(value, 0) + 1

    for tag_name, tag_info in tag_dict.items():
        unique_attributes: list[AttributeData] = []
        for attr_name, attr_info in tag_info["attributes"].items():
            vals = [ValueData(value=v, count=c) for v, c in attr_info["values"].items()]
            unique_attributes.append(
                AttributeData(attribute=attr_name, count=attr_info["count"], values=tuple(vals))
            )
        unique_html_tags.append(
            TagData(tag=tag_name, count=tag_info["count"], attributes=tuple(unique_attributes))
        )

    return tuple(unique_html_tags)


def _extract_link_contexts(
    plain_body: str, html_body: str
) -> tuple[tuple[str, ...], tuple[str, ...]]:
    """Find all links in HTML anchors and bare URLs.

    Args:
        plain_body: The email's plain-text body.
        html_body: The email's HTML body.

    Returns:
        A tuple containing the list of full URLs and the context of each URLs usage.
    """
    full_urls: list[str] = []
    contexts: list[str] = []

    if html_body:
        try:
            soup = bs4.BeautifulSoup(html_body, "html.parser")
        except bs4.exceptions.ParserRejectedMarkup:
            soup = bs4.BeautifulSoup(html_body, "html5lib")
        for a in soup.find_all("a", href=True):
            if not isinstance(a, bs4.Tag):
                continue
            full_urls.append(str(a["href"]))
            contexts.append(str(a))

    url_regex = re.compile(r'(https?://[^\s"<>\]]+)', re.IGNORECASE)
    for match in url_regex.finditer(plain_body):
        url = match.group(1)
        full_urls.append(url.rstrip("]>)},.;"))
        start, end = match.span(1)
        window = 30
        prefix = plain_body[max(0, start - window) : start]
        suffix = plain_body[end : end + window]
        contexts.append(f"{prefix}…{suffix}")

    return tuple(full_urls), tuple(contexts)


def serialize_email_data(email_data_list: list[EmailData], path: pathlib.Path) -> None:
    """Serialize a list of EmailData objects to a Parquet file.

    Args:
        email_data_list: List of EmailData objects to serialize.
        path: Path to the output Parquet file.
    """
    records = []
    for email_data in email_data_list:
        record = email_data.model_dump()
        record["unique_html_tags"] = json.dumps(
            [t.model_dump() for t in email_data.unique_html_tags]
        )
        record["link_domains"] = json.dumps(email_data.link_domains)
        record["link_contexts"] = json.dumps(email_data.link_contexts)
        records.append(record)
    email_dataframe = pd.DataFrame(records)
    email_dataframe.to_parquet(path, index=False)


def deserialize_email_data(path: pathlib.Path) -> list[EmailData]:
    """Deserialize a Parquet file into a list of EmailData objects.

    Args:
        path: Path to the Parquet file.

    Returns:
        List of EmailData objects reconstructed from file.
    """
    email_dataframe = pd.read_parquet(path)
    results = []
    for _, row in email_dataframe.iterrows():
        tags = tuple(TagData.model_validate(t) for t in json.loads(row["unique_html_tags"]))
        link_domains = tuple(json.loads(row["link_domains"]))
        link_contexts = tuple(json.loads(row["link_contexts"]))
        args = row.to_dict()
        args["unique_html_tags"] = tags
        args["link_domains"] = link_domains
        args["link_contexts"] = link_contexts
        results.append(EmailData.model_validate(args))
    return results
