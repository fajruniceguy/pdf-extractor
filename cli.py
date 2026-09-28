"""Page-by-page summary of what the extraction layer found in a PDF.

    python cli.py path/to/file.pdf

No LLM calls here — just a deterministic report of text blocks and
tables per page, for sanity-checking the extraction layer itself.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from extractor import Document, extract_pdf


def summarize(document: Document) -> str:
    lines = [
        f"Document: {document.doc_id} ({document.page_count} pages)",
        f"Path: {document.path}",
        "",
    ]
    for page in document.pages:
        char_count = sum(len(block.text) for block in page.text_blocks)
        lines.append(
            f"Page {page.page}: {len(page.text_blocks)} text blocks, "
            f"{char_count} characters, {len(page.tables)} tables"
        )
        for i, table in enumerate(page.tables, start=1):
            rows = len(table.rows)
            cols = len(table.rows[0]) if rows else 0
            lines.append(f"  Table {i}: {rows} rows x {cols} cols")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
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
