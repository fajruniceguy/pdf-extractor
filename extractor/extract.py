"""PDF extraction: native text and tables, mapped to page numbers.

Uses pdfplumber only. No OCR, no LLM calls — this layer is purely
deterministic, per the project's scope (see Claude.md).
"""
from __future__ import annotations

import math
import re
from dataclasses import dataclass
from pathlib import Path

import pdfplumber
from pdfplumber.page import Page

from .models import Document, PageContent, Table, TextBlock

# Experimental column-aware reading order; off unless extract_pdf(column_aware=True).
MIN_COLUMN_WORDS = 40  # fewer words than this is not enough evidence of columns
MIN_COLUMN_SIDE_FRACTION = 0.25  # each column must hold at least this share of the words
MIN_GUTTER_PT = 3.0  # empty vertical band between the columns; pdfplumber merges words closer than 3pt
LINE_Y_TOLERANCE = 3.0  # pdfplumber's default for grouping words into lines
MIN_TABLE_AMOUNTS = 5  # dot-grouped amounts needed on EACH side of the gutter to treat the page as a table
_AMOUNT = re.compile(r"^\(?\d{1,3}(?:\.\d{3})+\)?$")  # e.g. 13.045.179 or (516.544)


def extract_pdf(path: str | Path, *, column_aware: bool = False) -> Document:
    path = Path(path)
    extract_blocks = _extract_text_blocks_columns if column_aware else _extract_text_blocks
    pages: list[PageContent] = []
    with pdfplumber.open(path) as pdf:
        for page_number, page in enumerate(pdf.pages, start=1):
            pages.append(
                PageContent(
                    page=page_number,
                    text_blocks=extract_blocks(page, page_number),
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


@dataclass(frozen=True)
class ColumnAnalysis:
    two_columns: bool
    reason: str
    gutter: tuple[float, float] | None = None  # (left cluster's right edge, right cluster's left edge)
    left_words: int = 0
    right_words: int = 0


def analyze_columns(words: list[dict]) -> ColumnAnalysis:
    """Split word x-midpoints into two clusters at the widest gap; two columns only if the clusters have an empty gutter between them."""
    n = len(words)
    if n < MIN_COLUMN_WORDS:
        return ColumnAnalysis(False, f"only {n} words, need {MIN_COLUMN_WORDS}")
    mids = sorted((w["x0"] + w["x1"]) / 2 for w in words)
    side = math.ceil(MIN_COLUMN_SIDE_FRACTION * n)
    split = max(range(side - 1, n - side), key=lambda i: mids[i + 1] - mids[i])
    left = [w for w in words if (w["x0"] + w["x1"]) / 2 <= mids[split]]
    right = [w for w in words if (w["x0"] + w["x1"]) / 2 > mids[split]]
    if not left or not right:
        return ColumnAnalysis(False, "degenerate split: all word midpoints coincide")
    gutter = (max(w["x1"] for w in left), min(w["x0"] for w in right))
    width = gutter[1] - gutter[0]
    if width < MIN_GUTTER_PT:
        reason = f"no clear gutter: {width:.1f}pt between the two clusters, need {MIN_GUTTER_PT:g}pt"
        return ColumnAnalysis(False, reason, gutter, len(left), len(right))
    return ColumnAnalysis(True, f"two columns, gutter {width:.1f}pt", gutter, len(left), len(right))


def has_table_amounts(words: list[dict], gutter: tuple[float, float]) -> bool:
    """True when amounts sit on both sides of the gutter, i.e. splitting would separate a table row's figures."""
    cut = sum(gutter) / 2
    left = sum(bool(_AMOUNT.match(w["text"])) for w in words if (w["x0"] + w["x1"]) / 2 < cut)
    right = sum(bool(_AMOUNT.match(w["text"])) for w in words if (w["x0"] + w["x1"]) / 2 >= cut)
    return left >= MIN_TABLE_AMOUNTS and right >= MIN_TABLE_AMOUNTS


def _extract_text_blocks_columns(page: Page, page_number: int) -> list[TextBlock]:
    """Experimental: a clearly two-column, non-table page is read as its left column, then its right column."""
    words = page.extract_words()
    analysis = analyze_columns(words)
    if not analysis.two_columns or has_table_amounts(words, analysis.gutter):
        return _extract_text_blocks(page, page_number)
    cut = sum(analysis.gutter) / 2
    left = [w for w in words if (w["x0"] + w["x1"]) / 2 < cut]
    right = [w for w in words if (w["x0"] + w["x1"]) / 2 >= cut]
    return _words_to_blocks(left, page_number) + _words_to_blocks(right, page_number)


def _words_to_blocks(words: list[dict], page_number: int) -> list[TextBlock]:
    lines: list[list[dict]] = []
    for word in sorted(words, key=lambda w: (w["top"], w["x0"])):
        if lines and word["top"] - lines[-1][-1]["top"] <= LINE_Y_TOLERANCE:
            lines[-1].append(word)
        else:
            lines.append([word])
    blocks = []
    for line in lines:
        line.sort(key=lambda w: w["x0"])
        text = " ".join(w["text"] for w in line).strip()
        if not text:
            continue
        bbox = (
            min(w["x0"] for w in line),
            min(w["top"] for w in line),
            max(w["x1"] for w in line),
            max(w["bottom"] for w in line),
        )
        blocks.append(TextBlock(page=page_number, text=text, bbox=bbox))
    return blocks
