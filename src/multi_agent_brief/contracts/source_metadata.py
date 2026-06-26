"""Shared source metadata validation helpers."""

from __future__ import annotations

import re
from typing import Any, Mapping
from urllib.parse import urlparse

SOURCE_CATEGORY_FIELD = "source_category"
VALID_SOURCE_CATEGORIES = {
    "clin" + "ical_registry",
    "company_press_release",
    "industry_database",
    "market_report",
    "news_media",
    "other",
    "peer_reviewed_paper",
    "preprint",
    "regulator",
}
VALID_RETRIEVAL_SOURCE_TYPES = {
    "blog",
    "company_pr",
    "dataset",
    "filing",
    "local_file",
    "news_media",
    "other",
    "paper_page",
    "podcast",
    "social",
    "video",
}
VALID_UNDERLYING_EVIDENCE_TYPES = {
    "company_claim",
    "conference_demo",
    "filing",
    "interview",
    "market_data",
    "media_report",
    "peer_reviewed_paper",
    "regulator_record",
    "unknown",
}
SOURCE_CATEGORY_ALIASES = {
    "company_claim": "company_press_release",
    "company_official": "company_press_release",
    "company_pr": "company_press_release",
    "company_release": "company_press_release",
    "company_source": "company_press_release",
    "data_provider": "industry_database",
    "government_regulator": "regulator",
    "industry_media": "news_media",
    "industry_news": "news_media",
    "industry_report": "market_report",
    "market_data": "industry_database",
    "market_data_provider": "industry_database",
    "media": "news_media",
    "media_report": "news_media",
    "news": "news_media",
    "official_regulator": "regulator",
    "paper": "peer_reviewed_paper",
    "regulator_record": "regulator",
    "regulatory": "regulator",
    "research_institution": "market_report",
    "research_report": "market_report",
    "trade_publication": "news_media",
}
RETRIEVAL_SOURCE_TYPE_ALIASES = {
    "academic_paper": "paper_page",
    "article": "news_media",
    "cached": "local_file",
    "cached_package": "local_file",
    "company_blog": "blog",
    "company_official": "company_pr",
    "company_release": "company_pr",
    "company_source": "company_pr",
    "government_regulator": "other",
    "industry_media": "news_media",
    "industry_news": "news_media",
    "local": "local_file",
    "manual": "local_file",
    "manual_url": "other",
    "market_data": "dataset",
    "market_data_provider": "dataset",
    "media": "news_media",
    "news": "news_media",
    "official_regulator": "other",
    "paper": "paper_page",
    "preprint": "paper_page",
    "regulator_record": "other",
    "regulatory": "other",
    "research_report": "paper_page",
    "sec_filing": "filing",
    "trade_publication": "news_media",
}
UNDERLYING_EVIDENCE_TYPE_ALIASES = {
    "academic_paper": "peer_reviewed_paper",
    "company_press_release": "company_claim",
    "company_official": "company_claim",
    "company_pr": "company_claim",
    "company_release": "company_claim",
    "company_source": "company_claim",
    "data_provider": "market_data",
    "government_regulator": "regulator_record",
    "industry_database": "market_data",
    "industry_media": "media_report",
    "industry_news": "media_report",
    "market_data_provider": "market_data",
    "market_report": "market_data",
    "media": "media_report",
    "news": "media_report",
    "news_media": "media_report",
    "official_regulator": "regulator_record",
    "paper": "peer_reviewed_paper",
    "press_release": "company_claim",
    "regulator": "regulator_record",
    "regulatory": "regulator_record",
    "research_institution": "market_data",
    "research_report": "media_report",
    "sec_filing": "filing",
    "trade_publication": "media_report",
}


def non_empty_text(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def source_url_error(value: Any) -> str | None:
    if value is None or value == "":
        return None
    if not isinstance(value, str):
        return "must be a string"
    stripped = value.strip()
    if not stripped:
        return None
    try:
        parsed = urlparse(stripped)
    except ValueError:
        return "must be an http(s) URL"
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        return "must be an http(s) URL"
    return None


def source_category_error(value: Any) -> str | None:
    if value is None or value == "":
        return None
    if not isinstance(value, str):
        return "must be a string"
    if value.strip() not in VALID_SOURCE_CATEGORIES:
        return f"must be one of {sorted(VALID_SOURCE_CATEGORIES)}"
    return None


def retrieval_source_type_error(value: Any) -> str | None:
    if value is None or value == "":
        return None
    if not isinstance(value, str):
        return "must be a string"
    if value.strip() not in VALID_RETRIEVAL_SOURCE_TYPES:
        return f"must be one of {sorted(VALID_RETRIEVAL_SOURCE_TYPES)}"
    return None


def underlying_evidence_type_error(value: Any) -> str | None:
    if value is None or value == "":
        return None
    if not isinstance(value, str):
        return "must be a string"
    if value.strip() not in VALID_UNDERLYING_EVIDENCE_TYPES:
        return f"must be one of {sorted(VALID_UNDERLYING_EVIDENCE_TYPES)}"
    return None


def normalize_source_category(*values: Any, default: str = "other") -> str:
    for value in values:
        normalized = _taxonomy_key(value)
        if not normalized:
            continue
        if normalized in VALID_SOURCE_CATEGORIES:
            return normalized
        if normalized in SOURCE_CATEGORY_ALIASES:
            return SOURCE_CATEGORY_ALIASES[normalized]
    return default


def normalize_retrieval_source_type(*values: Any, default: str = "other") -> str:
    for value in values:
        normalized = _taxonomy_key(value)
        if not normalized:
            continue
        if normalized in VALID_RETRIEVAL_SOURCE_TYPES:
            return normalized
        if normalized in RETRIEVAL_SOURCE_TYPE_ALIASES:
            return RETRIEVAL_SOURCE_TYPE_ALIASES[normalized]
    return default


def normalize_underlying_evidence_type(*values: Any, default: str = "unknown") -> str:
    for value in values:
        normalized = _taxonomy_key(value)
        if not normalized:
            continue
        if normalized in VALID_UNDERLYING_EVIDENCE_TYPES:
            return normalized
        if normalized in UNDERLYING_EVIDENCE_TYPE_ALIASES:
            return UNDERLYING_EVIDENCE_TYPE_ALIASES[normalized]
    return default


def _taxonomy_key(value: Any) -> str:
    if not isinstance(value, str):
        return ""
    return re.sub(r"[^a-z0-9]+", "_", value.strip().lower()).strip("_")


def has_valid_source_url(record: Mapping[str, Any]) -> bool:
    value = record.get("source_url")
    return non_empty_text(value) and source_url_error(value) is None


def source_category_missing(record: Mapping[str, Any]) -> bool:
    return not non_empty_text(record.get(SOURCE_CATEGORY_FIELD))


def local_file_without_url_missing_identity(
    record: Mapping[str, Any],
    *,
    default_source_type: str | None = None,
) -> str | None:
    source_type = record.get("source_type")
    if isinstance(source_type, str):
        normalized_source_type = source_type.strip() or default_source_type
    elif source_type is None:
        normalized_source_type = default_source_type
    else:
        return None
    if not normalized_source_type:
        return None
    if normalized_source_type != "local_file":
        return None
    if has_valid_source_url(record):
        return None
    if source_category_missing(record):
        return SOURCE_CATEGORY_FIELD
    if not (
        non_empty_text(record.get("source_title")) or non_empty_text(record.get("source_name"))
    ):
        return "source_title_or_source_name"
    return None
