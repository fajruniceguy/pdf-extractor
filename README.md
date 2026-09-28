# pdf-extractor

A document extraction and question-answering system for dense PDFs, built for workflows where a wrong answer is worse than no answer.

## Design principle

Every returned value must be traceable to its source page. If the answer isn't stated in the document, the system says "not stated" rather than inferring one. This governs every design decision in the project, including how confidence is computed (never a self-reported number from the model) and how retrieval is structured (page numbers live in the same table row as the embeddings, so a chunk can't be returned without its source).

## What's implemented

- **PDF extraction** (`extractor/`): per-page text and table extraction via `pdfplumber`, with every text block and table tagged with its page number. No OCR, no LLM calls — this layer is purely deterministic. Run it with `python cli.py path/to/file.pdf` for a page-by-page summary.
- **Database schema** (`migrations/001_initial_schema.sql`): PostgreSQL + pgvector schema for documents and chunks, with an HNSW index for cosine similarity search. Brought up via `docker compose up -d`.

## What's planned

- Chunking (~800 chars, 150 overlap, page number preserved) and embedding of extracted text
- Vector retrieval (top-k similarity search over stored chunks)
- Answer generation layer with mandatory page citations and a `not_stated` / `low_confidence` status
- Eval suite: 30-50 labeled question/answer/page triples, including questions with no answer in the document, reporting answer accuracy, citation page accuracy, and correct `not_stated` rate

## Running it

Requirements: Docker, Python 3.11+.

```bash
# start Postgres + pgvector (applies the schema on first run)
docker compose up -d

# install dependencies
pip install -r requirements.txt

# run extraction on a PDF
python cli.py path/to/file.pdf
```

Copy `.env.example` to `.env` and fill in real values once the embedding/answer layers land — they aren't wired up yet, so no keys are required for the extraction step above.

## Known issues

- `find_tables` (pdfplumber) produces false positives on 1x2 and 2x1 bordered regions, so small bordered boxes can be misdetected as tables. Not yet fixed.
