# pdf-extractor

A document extraction and question-answering system for dense PDFs, built for workflows where a wrong answer is worse than no answer.

## Design principle

Every returned value must be traceable to its source page. If the answer isn't stated in the document, the system says "not stated" rather than inferring one. This governs every design decision in the project, including how confidence is computed (never a self-reported number from the model) and how retrieval is structured (page numbers live in the same table row as the embeddings, so a chunk can't be returned without its source).

## What's implemented

- **PDF extraction** (`extractor/extract.py`): per-page text and table extraction via `pdfplumber`, with every text block and table tagged with its page number. No OCR, no LLM calls — this layer is purely deterministic.
- **Chunking** (`extractor/chunk.py`): splits each page's text into ~800 char chunks with 150 char overlap. Chunks never span pages, so a chunk's page number is always exact, never a guess about which page it "mostly" belongs to.
- **Database schema** (`migrations/001_initial_schema.sql`): PostgreSQL + pgvector schema for documents and chunks, with an HNSW index for cosine similarity search. Brought up via `docker compose up -d`.

Run `python cli.py path/to/file.pdf` to see extraction + chunking together, page by page.

## RAG implementation plan

Nothing below this line is built yet — the schema and prompting rules are designed for it, but there's no embedding, retrieval, or generation code in the repo. This is the order it'll be built in:

1. **Embed chunks** — `text-embedding-3-small` (1536 dims, matches `chunks.embedding`). Check for existing chunks before embedding so re-running ingestion never re-embeds for free; embeddings are a one-time cost per document.
2. **Store** — insert each chunk's page number, content, and embedding into `chunks`, one row per chunk, one `documents` row per source PDF.
3. **Retrieve** — embed the incoming question, then cosine-similarity search (`ORDER BY embedding <=> query LIMIT 5`) scoped to a `document_id`. This is already written as SQL in `Claude.md`; it just needs to be called from code.
4. **Generate** — Claude Haiku 4.5 receives only the retrieved chunks as context (no general knowledge) and returns a `not_stated` status when the context doesn't contain the answer. Response is validated against a `Answer`/`Citation` Pydantic model — every answer carries at least one page citation.
5. **Confidence** — derived, not self-reported: retrieval similarity score + a model-returned boolean (`explicitly_stated` vs. inferred). `needs_review` fires when similarity is below threshold *or* the answer wasn't explicitly stated. The model is never asked to output a confidence number directly — LLMs are poorly calibrated at that.
6. **Eval suite** — 30-50 labeled question/answer/page triples, including questions with no answer in the document. Reports three metrics: answer accuracy, citation page accuracy, and correct `not_stated` rate on the absent-answer questions. Re-run after any change to chunking, retrieval, or prompting.

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
