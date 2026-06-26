"""Contract for SourceItem."""

from __future__ import annotations

from typing import Any, ClassVar

from multi_agent_brief.contracts.base import Contract, SchemaRegistry
from multi_agent_brief.contracts.errors import FieldViolation
from multi_agent_brief.contracts.source_metadata import (
    VALID_RETRIEVAL_SOURCE_TYPES,
    VALID_SOURCE_CATEGORIES,
    VALID_UNDERLYING_EVIDENCE_TYPES,
    retrieval_source_type_error,
    source_category_error,
    underlying_evidence_type_error,
)

REQUIRED_FIELDS = {"source_id", "source_name", "source_type", "title", "content"}
OPTIONAL_FIELDS = {
    "url",
    "published_at",
    "retrieved_at",
    "language",
    "reliability",
    "dedupe_key",
    "source_category",
    "retrieval_source_type",
    "underlying_evidence_type",
    "raw_underlying_evidence_type",
    "metadata",
}
ALL_FIELDS = REQUIRED_FIELDS | OPTIONAL_FIELDS


@SchemaRegistry.register
class SourceItemContract(Contract):
    schema_id: ClassVar[str] = "source_item"
    schema_version: ClassVar[str] = "v1"

    @classmethod
    def json_schema(cls) -> dict[str, Any]:
        return {
            "type": "object",
            "required": sorted(REQUIRED_FIELDS),
            "properties": {
                "source_id": {"type": "string"},
                "source_name": {"type": "string"},
                "source_type": {"type": "string"},
                "title": {"type": "string"},
                "content": {"type": "string"},
                "url": {"type": "string"},
                "published_at": {"type": "string"},
                "retrieved_at": {"type": "string"},
                "language": {"type": "string"},
                "reliability": {"type": "string", "enum": ["low", "medium", "high"]},
                "dedupe_key": {"type": "string"},
                "source_category": {"type": "string", "enum": sorted(VALID_SOURCE_CATEGORIES)},
                "retrieval_source_type": {
                    "type": "string",
                    "enum": sorted(VALID_RETRIEVAL_SOURCE_TYPES),
                },
                "underlying_evidence_type": {
                    "type": "string",
                    "enum": sorted(VALID_UNDERLYING_EVIDENCE_TYPES),
                },
                "raw_underlying_evidence_type": {"type": "string"},
                "metadata": {"type": "object"},
            },
            "additionalProperties": True,
        }

    @classmethod
    def validate(cls, data: dict[str, Any]) -> list[FieldViolation]:
        violations: list[FieldViolation] = []
        for field in REQUIRED_FIELDS:
            val = data.get(field)
            if val is None or (isinstance(val, str) and not val.strip()):
                violations.append(FieldViolation(field=field, error="required field is missing or blank"))
        category_error = source_category_error(data.get("source_category"))
        if category_error:
            violations.append(FieldViolation(field="source_category", error=category_error))
        retrieval_error = retrieval_source_type_error(data.get("retrieval_source_type"))
        if retrieval_error:
            violations.append(FieldViolation(field="retrieval_source_type", error=retrieval_error))
        underlying_error = underlying_evidence_type_error(data.get("underlying_evidence_type"))
        if underlying_error:
            violations.append(FieldViolation(field="underlying_evidence_type", error=underlying_error))
        # Unknown fields as warnings
        unknown = set(data.keys()) - ALL_FIELDS
        for field in sorted(unknown):
            violations.append(FieldViolation(field=field, error="unknown field", severity="warning"))
        return violations

    @classmethod
    def migrate(cls, data: dict[str, Any], from_version: str) -> dict[str, Any]:
        return dict(data)  # no migration needed for v1
