"""Tests for functions for the data IO module."""

from __future__ import annotations

import json
import pathlib

import pandas as pd
import pytest

from email_spam_filter.data.io import (
    create_email_data,
    deserialize_email_data,
    serialize_email_data,
)


@pytest.fixture
def eml_fixture() -> bytes:
    path = pathlib.Path(__file__).parents[1] / "example_email.eml"
    return path.read_bytes()


@pytest.fixture
def eml_file_path(tmp_path: pathlib.Path, eml_fixture: bytes) -> pathlib.Path:
    inbox_dir = tmp_path / "test_spam"
    inbox_dir.mkdir()
    eml_path = inbox_dir / "123_spam.eml"
    eml_path.write_bytes(eml_fixture)
    return eml_path


class TestEmailUtils:
    @staticmethod
    def test_create_email_data(eml_file_path: pathlib.Path) -> None:
        email_data = create_email_data(eml_file_path)

        assert email_data.id == 123
        assert email_data.tag == "spam"
        assert email_data.source == "test"

        assert email_data.subject.startswith("ACTION REQUIRED")
        assert email_data.from_addr == "john_mcafee@examplemail.com"
        assert "Example Security Team" in email_data.from_name

        assert email_data.n_rcpts == 1
        assert email_data.has_attach is False
        assert email_data.auth_fail is False

        assert email_data.n_links == 2
        assert email_data.n_dupe_links == 0
        assert "security.example.org" in email_data.link_domains
        assert set(email_data.link_domains) == {"security.example.org"}
        assert len(email_data.link_contexts) == 2

        tag_names = {t.tag for t in email_data.unique_html_tags}
        for required in ("a", "div", "h3", "p"):
            assert required in tag_names

        a_tag_data = next(t for t in email_data.unique_html_tags if t.tag == "a")
        href_attr = next(attr for attr in a_tag_data.attributes if attr.attribute == "href")
        assert href_attr.count == 2
        href_values = {v.value for v in href_attr.values}  # noqa: PD011
        assert {
            "https://security.example.org/verify-license",
            "https://security.example.org/unsubscribe",
        } <= href_values
        style_attr = next(attr for attr in a_tag_data.attributes if attr.attribute == "style")
        assert style_attr.count == 1
        style_values = {v.value for v in style_attr.values}  # noqa: PD011
        assert "text-decoration:none;color:#0072d1" in style_values

    @staticmethod
    def test_serialize_deserialize_roundtrip(
        eml_file_path: pathlib.Path, tmp_path: pathlib.Path
    ) -> None:
        email_data = create_email_data(eml_file_path)

        out_path = tmp_path / "emails.parquet"
        serialize_email_data([email_data], out_path)

        assert out_path.exists()
        assert isinstance(pd.read_parquet(out_path), pd.DataFrame)

        deserialised = deserialize_email_data(out_path)
        assert len(deserialised) == 1

        original = json.dumps(email_data.model_dump(mode="json"), sort_keys=True)
        new = json.dumps(deserialised[0].model_dump(mode="json"), sort_keys=True)
        assert original == new
