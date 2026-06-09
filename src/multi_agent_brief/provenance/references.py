"""Reference extraction for provenance projection."""

from __future__ import annotations

import re
from dataclasses import dataclass


REFERENCE_PATTERN = re.compile(
    r"\[(?P<label>src|claim|c|source|s):(?P<ref>[A-Za-z0-9_.:-]+)\]",
    re.IGNORECASE,
)


@dataclass(frozen=True)
class NormalizedReference:
    raw_ref: str
    normalized_ref_type: str
    normalized_ref_id: str


def extract_references(
    text: str,
    *,
    known_claim_ids: set[str],
    known_source_ids: set[str],
) -> list[NormalizedReference]:
    refs: list[NormalizedReference] = []
    for match in REFERENCE_PATTERN.finditer(text):
        label = match.group("label").lower()
        ref_id = match.group("ref")
        raw = match.group(0)
        if label in {"claim", "c"}:
            refs.append(NormalizedReference(raw, "claim", ref_id))
            continue
        if label in {"source", "s"}:
            refs.append(NormalizedReference(raw, "source", ref_id))
            continue
        if ref_id in known_source_ids and ref_id not in known_claim_ids:
            refs.append(NormalizedReference(raw, "source", ref_id))
        else:
            refs.append(NormalizedReference(raw, "claim", ref_id))
    return refs
