"""Page-by-page summary of what the extraction layer found in a PDF.

    python cli.py path/to/file.pdf          # extraction report
    python cli.py ingest path/to/file.pdf   # embed and store in Postgres
    python cli.py ask "question" [--doc ID] # top 5 chunks with file, page and score
    python cli.py docs                      # list ingested documents and their ids

No LLM calls in the report — just a deterministic report of text blocks and
tables per page, for sanity-checking the extraction layer itself.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from extractor import Document, chunk_document, extract_pdf


def summarize(document: Document) -> str:
    chunks = chunk_document(document)
    lines = [
        f"Document: {document.doc_id} ({document.page_count} pages)",
        f"Path: {document.path}",
        f"Chunks: {len(chunks)} (~800 chars, 150 overlap, page-bounded)",
        "",
    ]
    for page in document.pages:
        char_count = sum(len(block.text) for block in page.text_blocks)
        page_chunks = [c for c in chunks if c.page == page.page]
        lines.append(
            f"Page {page.page}: {len(page.text_blocks)} text blocks, "
            f"{char_count} characters, {len(page.tables)} tables, "
            f"{len(page_chunks)} chunks"
        )
        for i, table in enumerate(page.tables, start=1):
            rows = len(table.rows)
            cols = len(table.rows[0]) if rows else 0
            lines.append(f"  Table {i}: {rows} rows x {cols} cols")
    return "\n".join(lines)


def _ingest_main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(prog="cli.py ingest", description="Embed a PDF and store it in Postgres.")
    parser.add_argument("pdf_path", type=Path, help="path to a native-text PDF")
    args = parser.parse_args(argv)

    if not args.pdf_path.exists():
        print(f"error: file not found: {args.pdf_path}", file=sys.stderr)
        return 1

    from extractor.ingest import ingest

    try:
        ingest(args.pdf_path)
    except RuntimeError as e:
        print(f"error: {e}", file=sys.stderr)
        return 1
    return 0


def _ask_main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(prog="cli.py ask", description="Show the top 5 chunks for a question.")
    parser.add_argument("question", help="the question to search for")
    parser.add_argument("--doc", type=int, default=None, help="restrict to one document id (see: cli.py docs)")
    args = parser.parse_args(argv)

    from extractor.retrieve import search

    sys.stdout.reconfigure(errors="replace")
    try:
        results = search(args.question, document_id=args.doc)
    except RuntimeError as e:
        print(f"error: {e}", file=sys.stderr)
        return 1

    for rank, r in enumerate(results, start=1):
        preview = " ".join(r.content.split())[:200]
        print(f"{rank}. [{r.filename}] page {r.page_number}  score {r.similarity:.3f}")
        print(f"   {preview}")
    return 0


def _docs_main() -> int:
    from extractor.retrieve import list_documents

    sys.stdout.reconfigure(errors="replace")
    try:
        documents = list_documents()
    except RuntimeError as e:
        print(f"error: {e}", file=sys.stderr)
        return 1

    if not documents:
        print("No documents ingested.")
        return 0
    print(f"{'id':>4}  {'pages':>5}  {'chunks':>6}  filename")
    for d in documents:
        pages = "?" if d.page_count is None else d.page_count
        print(f"{d.id:>4}  {pages:>5}  {d.chunk_count:>6}  {d.filename}")
    return 0


def main(argv: list[str] | None = None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    if argv and argv[0] == "ingest":
        return _ingest_main(argv[1:])
    if argv and argv[0] == "ask":
        return _ask_main(argv[1:])
    if argv and argv[0] == "docs":
        return _docs_main()

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("pdf_path", type=Path, help="path to a native-text PDF")
    args = parser.parse_args(argv)

    if not args.pdf_path.exists():
        print(f"error: file not found: {args.pdf_path}", file=sys.stderr)
        return 1

    document = extract_pdf(args.pdf_path)
    print(summarize(document))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
