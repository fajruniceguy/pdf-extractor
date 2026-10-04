"""Ingestion: PDF -> extract -> chunk -> embed -> Postgres, in one transaction.

A file is identified by its sha256. Re-ingesting the same bytes never
re-embeds and never inserts. documents.page_count is the extractor's true
page count, so pages that yielded no text are visible as a gap against chunks.
"""
from __future__ import annotations

import hashlib
from pathlib import Path

import psycopg
from pgvector import Vector

from .chunk import chunk_document
from .db import connect
from .embed import embed_texts
from .extract import extract_pdf


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def _existing_id(conn: psycopg.Connection, file_hash: str) -> int | None:
    row = conn.execute(
        "SELECT id FROM documents WHERE file_sha256 = %s", (file_hash,)
    ).fetchone()
    return row[0] if row else None


def ingest(pdf_path: str | Path) -> int:
    """Ingest a PDF and return its documents.id (existing id if already ingested)."""
    path = Path(pdf_path)
    file_hash = _sha256(path)

    with connect() as conn:
        existing = _existing_id(conn, file_hash)
        if existing is not None:
            print(f"already ingested: {path.name} (document id {existing})")
            return existing

        document = extract_pdf(path)
        chunks = chunk_document(document)

        if not chunks:
            raise RuntimeError(
                f"No extractable text in {path.name} ({document.page_count} pages). "
                "The document is likely scanned images, and OCR is not implemented."
            )
        for chunk in chunks:
            if not isinstance(chunk.page, int) or chunk.page < 1:
                raise RuntimeError(f"chunk without a valid page number: {chunk!r}")

        pages_with_chunks = {c.page for c in chunks}
        empty_pages = [p.page for p in document.pages if p.page not in pages_with_chunks]

        vectors, tokens = embed_texts([c.content for c in chunks])

        try:
            with conn.transaction():
                doc_id = conn.execute(
                    "INSERT INTO documents (filename, page_count, file_sha256, zero_chunk_pages) "
                    "VALUES (%s, %s, %s, %s) RETURNING id",
                    (path.name, document.page_count, file_hash, empty_pages),
                ).fetchone()[0]
                with conn.cursor() as cur:
                    cur.executemany(
                        "INSERT INTO chunks (document_id, page_number, content, embedding) "
                        "VALUES (%s, %s, %s, %s)",
                        [
                            (doc_id, c.page, c.content, Vector(v))
                            for c, v in zip(chunks, vectors)
                        ],
                    )
        except psycopg.errors.UniqueViolation:
            existing = _existing_id(conn, file_hash)
            print(f"already ingested: {path.name} (document id {existing})")
            return existing

    print(f"Ingested {path.name} as document id {doc_id}")
    print(f"  pages: {document.page_count}")
    print(f"  chunks inserted: {len(chunks)}")
    print(f"  pages with zero chunks: {empty_pages if empty_pages else 'none'}")
    print(f"  embedding tokens used: {tokens}")
    return doc_id
