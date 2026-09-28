"""PDF extraction: native text and tables, mapped to page numbers.

Uses pdfplumber only. No OCR, no LLM calls — this layer is purely
deterministic, per the project's scope (see Claude.md).
"""
from __future__ import annotations

from pathlib import Path

import pdfplumber
from pdfplumber.page import Page

from .models import Document, PageContent, Table, TextBlock


def extract_pdf(path: str | Path) -> Document:
    path = Path(path)
    pages: list[PageContent] = []
    with pdfplumber.open(path) as pdf:
        for page_number, page in enumerate(pdf.pages, start=1):
            pages.append(
                PageContent(
                    page=page_number,
                    text_blocks=_extract_text_blocks(page, page_number),
                    tables=_extract_tables(page, page_number),
                )
            )
    return Document(doc_id=path.stem, path=str(path), page_count=len(pages), pages=pages)


def _extract_text_blocks(page: Page, page_number: int) -> list[TextBlock]:
    blocks = []
    for line in page.extract_text_lines(layout=False):
        text = line["text"].strip()
        if not text:
            continue
        bbox = (line["x0"], line["top"], line["x1"], line["bottom"])
        blocks.append(TextBlock(page=page_number, text=text, bbox=bbox))
    return blocks


def _extract_tables(page: Page, page_number: int) -> list[Table]:
    tables = []
    for found in page.find_tables():
        rows = found.extract()
        if not rows:
            continue
        tables.append(Table(page=page_number, rows=rows, bbox=found.bbox))
    return tables
