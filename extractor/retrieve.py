"""Retrieval: embed a question and return the nearest chunks with their pages."""
from __future__ import annotations

from dataclasses import dataclass

from pgvector import Vector

from .db import connect
from .embed import embed_texts

# `<=>` is pgvector's cosine DISTANCE (0 = identical, 2 = opposite). Similarity is
# reported as 1 - distance, so HIGHER means MORE similar. ORDER BY distance ascending
# returns the best matches first and is the form the HNSW index can serve.
_SELECT = """
SELECT c.id, d.filename, c.page_number, c.content,
       1 - (c.embedding <=> %(q)s) AS similarity
FROM chunks c
JOIN documents d ON d.id = c.document_id
"""
_ORDER = """
ORDER BY c.embedding <=> %(q)s
LIMIT %(k)s
"""
SEARCH_SQL = _SELECT + _ORDER
SEARCH_SQL_ONE_DOC = _SELECT + "WHERE c.document_id = %(doc)s" + _ORDER


@dataclass(frozen=True)
class SearchResult:
    chunk_id: int
    filename: str
    page_number: int
    content: str
    similarity: float


@dataclass(frozen=True)
class DocumentSummary:
    id: int
    filename: str
    page_count: int | None
    chunk_count: int


def search(question: str, k: int = 5, document_id: int | None = None) -> list[SearchResult]:
    with connect() as conn:
        if not conn.execute("SELECT EXISTS (SELECT 1 FROM chunks)").fetchone()[0]:
            raise RuntimeError(
                "The chunks table is empty. Ingest a PDF first: python cli.py ingest file.pdf"
            )
        if document_id is not None and not conn.execute(
            "SELECT EXISTS (SELECT 1 FROM chunks WHERE document_id = %s)", (document_id,)
        ).fetchone()[0]:
            raise RuntimeError(
                f"No chunks for document id {document_id}. List ids with: python cli.py docs"
            )
        vectors, _ = embed_texts([question])
        params = {"q": Vector(vectors[0]), "k": k, "doc": document_id}
        sql = SEARCH_SQL if document_id is None else SEARCH_SQL_ONE_DOC
        rows = conn.execute(sql, params).fetchall()
    return [SearchResult(*row) for row in rows]


def list_documents() -> list[DocumentSummary]:
    with connect() as conn:
        rows = conn.execute(
            "SELECT d.id, d.filename, d.page_count, count(c.id) "
            "FROM documents d LEFT JOIN chunks c ON c.document_id = d.id "
            "GROUP BY d.id ORDER BY d.id"
        ).fetchall()
    return [DocumentSummary(*row) for row in rows]
