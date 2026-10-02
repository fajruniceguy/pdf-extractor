"""Data structures for extracted PDF content.

Every block carries its own `page` number so downstream consumers
never have to re-derive source attribution.
"""
from __future__ import annotations

from dataclasses import dataclass

BBox = tuple[float, float, float, float]


@dataclass(frozen=True)
class TextBlock:
    page: int
    text: str
    bbox: BBox


@dataclass(frozen=True)
class Table:
    page: int
    rows: list[list[str | None]]
    bbox: BBox


@dataclass(frozen=True)
class PageContent:
    page: int
    text_blocks: list[TextBlock]
    tables: list[Table]

    @property
    def text(self) -> str:
        return "\n".join(block.text for block in self.text_blocks)


@dataclass(frozen=True)
class Document:
    doc_id: str
    path: str
    page_count: int
    pages: list[PageContent]


@dataclass(frozen=True)
class Chunk:
    page: int
    content: str
