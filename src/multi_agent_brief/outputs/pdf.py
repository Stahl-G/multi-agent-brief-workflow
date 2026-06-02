from __future__ import annotations

from dataclasses import dataclass


@dataclass
class PdfOutputRequest:
    markdown_path: str
    output_path: str
    stylesheet_path: str = ""


class PdfOutputAdapter:
    """Migration-track interface for PDF generation."""

    name = "pdf"

    def render(self, request: PdfOutputRequest) -> str:
        raise RuntimeError("PDF output is a migration-track interface and is not implemented in the MVP.")

