"""Shared helpers for internal claim citation markers."""

from __future__ import annotations

import re


CLAIM_ID_RE_FRAGMENT = r"[A-Za-z0-9][A-Za-z0-9_-]{1,127}"
SRC_REF_PATTERN = re.compile(rf"\[src:({CLAIM_ID_RE_FRAGMENT})\]")
VALID_SRC_REF_PATTERN = re.compile(rf"\[src:{CLAIM_ID_RE_FRAGMENT}\]")


def extract_src_ref_ids(markdown: str) -> list[str]:
    return SRC_REF_PATTERN.findall(markdown)
