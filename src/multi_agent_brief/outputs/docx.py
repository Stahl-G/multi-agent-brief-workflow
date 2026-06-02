from __future__ import annotations

from dataclasses import dataclass


@dataclass
class DocxOutputRequest:
    markdown_path: str
    output_path: str
    template_path: str = ""


class DocxOutputAdapter:
    """Migration-track interface for DOCX generation."""

    name = "docx"

    def render(self, request: DocxOutputRequest) -> str:
        raise RuntimeError("DOCX output is a migration-track interface and is not implemented in the MVP.")

