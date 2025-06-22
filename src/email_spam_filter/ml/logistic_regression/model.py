"""Defines the logistic regression pipeline architecture."""

from __future__ import annotations

from sklearn.feature_extraction import DictVectorizer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import FeatureUnion, Pipeline
from sklearn.preprocessing import FunctionTransformer, StandardScaler

from email_spam_filter.ml.logistic_regression.functions import extract_html_features


def model() -> Pipeline:
    """Build and return a logistic regression classification pipeline."""
    # Text pipe: combine subject + body text, then tokenise and vectorise
    text_pipe = Pipeline(
        [
            (
                "combine_text",
                FunctionTransformer(
                    func=lambda df: df["subject"] + " " + df["body"],
                    validate=False,
                    feature_names_out=lambda _transformer, _input_features: ["combined_text"],
                ),
            ),
            (
                "tfidf",
                TfidfVectorizer(
                    token_pattern=r"(?u)\b[A-Za-z][A-Za-z0-9]+\b",  # noqa: S106
                ),
            ),
        ]
    )

    # HTML pipe: extract HTML features then vectorise
    html_pipe = Pipeline(
        [
            (
                "extract_html",
                FunctionTransformer(
                    func=lambda df: extract_html_features(df["unique_html_tags"]),
                    validate=False,
                    feature_names_out=lambda _transformer, _input_features: ["html_features"],
                ),
            ),
            ("vect_html", DictVectorizer()),
        ]
    )

    # Meta numeric pipe: select and scale numeric metadata
    meta_numeric = Pipeline(
        [
            (
                "select_numeric",
                FunctionTransformer(
                    func=lambda df: df[["n_links", "n_dupe_links", "n_rcpts"]].astype(float),
                    validate=False,
                    feature_names_out=lambda _transformer, _input_features: [
                        "n_links",
                        "n_dupe_links",
                        "n_rcpts",
                    ],
                ),
            ),
            ("scale_numeric", StandardScaler()),
        ]
    )
    # Meta boolean pipe: cast boolean metadata to int (0/1)
    meta_bool = FunctionTransformer(
        func=lambda df: df[["has_attach", "auth_fail"]].astype(int),
        validate=False,
        feature_names_out=lambda _transformer, _input_features: ["has_attach", "auth_fail"],
    )
    # Meta pipe: combine numeric and boolean metadata pipes
    meta_pipe = FeatureUnion(
        [
            ("numeric", meta_numeric),
            ("bool", meta_bool),
        ]
    )

    # Domain pipe: extract sender domain, then tokenise and vectorise
    domain_pipe = Pipeline(
        [
            (
                "extract_domain",
                FunctionTransformer(
                    lambda df: df["from_addr"].str.split("@").str[-1],
                    validate=False,
                    feature_names_out=lambda _transformer, _input_features: ["sender_domain"],
                ),
            ),
            (
                "char_ngrams",
                TfidfVectorizer(analyzer="char_wb", ngram_range=(3, 5), max_features=256),
            ),
        ]
    )

    # Features: Collection of different pipes
    features = FeatureUnion(
        [
            ("text", text_pipe),
            ("html", html_pipe),
            ("meta", meta_pipe),
            ("domain", domain_pipe),
        ],
        transformer_weights={
            "text": 0.50,
            "html": 1.0,
            "meta": 1.0,
            "domain": 0.25,
        },
    )

    # Final pipeline: features + classifier
    return Pipeline(
        [
            ("features", features),
            ("classifier", LogisticRegression(max_iter=1000)),
        ]
    )
