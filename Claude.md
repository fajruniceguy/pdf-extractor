# CLAUDE.md

Project context for Claude Code. Read this before making changes.

## What this is

A document extraction and question-answering system for dense PDFs, built for workflows where a wrong answer is worse than no answer.

The design principle that governs everything: **every returned value must be traceable to its source page, and the system must say "not stated" rather than infer.** If a change would weaken traceability or make the system guess, don't make it.

This is a portfolio project targeting AI Engineer roles. Code quality and defensible design decisions matter more than feature count.

## Stack

- Python 3.11+
- FastAPI (serving) — **not Django**, this was a deliberate switch
- PostgreSQL 16 + pgvector (relational data and embeddings in one place, no separate vector DB)
- Pydantic v2 (validation and OpenAPI schema generation)
- OpenAI `text-embedding-3-small` (embeddings, 1536 dimensions)
- Anthropic `claude-haiku-4-5-20251001` (answer generation)
- Docker / docker-compose

## Architecture

**Ingestion:** PDF → per-page text extraction → chunking (~800 chars, 150 overlap, page number preserved) → embedding → Postgres.

**Query:** question → embed → cosine similarity search → top-5 chunks with page numbers → LLM with chunks as context → validated JSON response.

The page number lives in the same table row as the embedding. Retrieval therefore cannot return a chunk without returning where it came from. Do not restructure this into separate tables or a separate vector store.

## Schema

```sql
CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE documents (
  id          SERIAL PRIMARY KEY,
  filename    TEXT NOT NULL,
  page_count  INT,
  created_at  TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE chunks (
  id           SERIAL PRIMARY KEY,
  document_id  INT NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
  page_number  INT NOT NULL,
  content      TEXT NOT NULL,
  embedding    vector(1536)
);

CREATE INDEX ON chunks USING hnsw (embedding vector_cosine_ops);
```

`vector(1536)` must match the embedding model's dimension. Changing embedding models requires re-embedding every chunk — flag this before doing it.

## Retrieval

```sql
SELECT page_number, content,
       1 - (embedding <=> %(q)s) AS similarity
FROM chunks
WHERE document_id = %(doc)s
ORDER BY embedding <=> %(q)s
LIMIT 5;
```

`<=>` is pgvector's cosine distance operator. Lower is closer, so `ORDER BY` ascending returns best matches first.

## Response contract

```python
from pydantic import BaseModel, Field
from typing import Literal

class Citation(BaseModel):
    page: int
    snippet: str

class Answer(BaseModel):
    status: Literal["answered", "not_stated", "low_confidence"]
    value: str | None
    confidence: float = Field(ge=0, le=1)
    citations: list[Citation]
    needs_review: bool
```

This model is both runtime validation and the auto-generated OpenAPI schema. Do not bypass it or return raw dicts from endpoints.

## Confidence design — do not change without discussion

**Never ask the model to self-report confidence as a number.** LLMs are poorly calibrated at this.

Confidence is derived from two signals:
1. Retrieval similarity score from pgvector
2. A boolean from the model: was the answer explicitly stated in the provided context, or inferred?

`needs_review` fires when similarity is below threshold **or** `explicitly_stated` is false.

This is the most defensible design decision in the project. Preserve it.

## Prompting rules

- The answer model receives only retrieved chunks as context. It must not answer from general knowledge.
- It must return `not_stated` when the context does not contain the answer. This is correct behavior, not a failure.
- Every returned value must carry at least one citation with a page number.
- Always set `max_tokens` (500 is sufficient). Output is priced at 5x input.

## Cost discipline

- Embeddings are one-time per document. Never re-embed on every run — check whether chunks already exist.
- Use Haiku 4.5 for answers. Do not upgrade to a frontier model without a measured eval reason.
- Use the Batch API for eval runs (50% discount, async is fine there).
- Any retry logic needs a hard cap. Runaway loops are the only real cost risk.
- Print cumulative token usage after each run.

## Secrets

API keys come from environment variables only. Never hardcode, never commit, never log them.

## Evals

The eval suite is the point, not an afterthought — it produces the accuracy number this project is judged on.

- 30-50 labeled question / expected-answer / expected-page triples
- **Must include questions whose answers are genuinely absent from the document.** A system that never returns `not_stated` is a confident liar.
- Report three metrics: answer accuracy, citation page accuracy, correct `not_stated` rate on absent questions.
- Re-run evals after any change to chunking, retrieval, or prompting. Regressions here matter more than passing unit tests.

## Working style

- Incremental changes, verify each one, commit before moving on.
- Run the evals before and after any change to the retrieval or answer path.
- Don't add dependencies without saying why.
- Don't add features that aren't in the current step.
- When something breaks, surface the actual error rather than working around it.

## Known issues

- `find_tables` produces false positives on 1x2 and 2x1 bordered regions. Not yet fixed.

## Out of scope

Django, authentication, multi-tenancy, a frontend, and any model fine-tuning. If a change requires one of these, stop and ask first.