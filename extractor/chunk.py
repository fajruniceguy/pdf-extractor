"""Chunking: splits each page's extracted text into fixed-size, overlapping
chunks, carrying the page number over unchanged.

Chunks never span pages. The page_number on a chunk must be exact per the
project's traceability principle (see Claude.md), not a guess about which
page a cross-boundary chunk "mostly" belongs to.
"""
from __future__ import annotations

from .models import Chunk, Document

CHUNK_SIZE = 800
CHUNK_OVERLAP = 150


def chunk_document(document: Document) -> list[Chunk]:
    chunks: list[Chunk] = []
    for page in document.pages:
        chunks.extend(_chunk_text(page.text, page.page))
    return chunks


def _chunk_text(text: str, page_number: int) -> list[Chunk]:
    if not text:
        return []
    if len(text) <= CHUNK_SIZE:
        return [Chunk(page=page_number, content=text)]

    chunks = []
    step = CHUNK_SIZE - CHUNK_OVERLAP
    start = 0
    while start < len(text):
        end = start + CHUNK_SIZE
        chunks.append(Chunk(page=page_number, content=text[start:end]))
        if end >= len(text):
            break
        start += step
    return chunks
