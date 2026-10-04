# pdf-extractor

A document extraction and question-answering system for dense PDFs, built for workflows where a wrong answer is worse than no answer.

## Design principle

Every returned value must be traceable to its source page. If the answer isn't stated in the document, the system says "not stated" rather than inferring one. Page numbers live in the same table row as the embeddings, so a chunk can't be returned without its source, and every answer must cite `[filename, page N]`. That is the goal. The wrong-entity answer documented under [Measured results](#measured-results) is a case where the system does not meet it.

## Status

A working command-line pipeline: **ingest a PDF, search it, get a cited answer or "not stated"**. It has been run on four real documents with very different layouts (a 42-page technical paper, a 7-page research note, a 25-page whitepaper, and a 152-page bilingual interim financial report), and each extracts differently: the whitepaper cleanly, the others with run-together words and garbled glyphs, mirrored text, or interleaved bilingual columns. It is a prototype: there is no API, no automated tests, and the confidence design below is not built yet. The failure modes found so far are listed under [Known issues](#known-issues).

## What works

- **Extraction** (`extractor/extract.py`): per-page text and tables via `pdfplumber`, every block tagged with its page number. Deterministic, no OCR, no LLM calls.
- **Chunking** (`extractor/chunk.py`): ~800 characters with 150 overlap. Chunks never span pages, so a chunk's page number is always exact.
- **Ingestion** (`extractor/ingest.py`): extract, chunk, embed (`text-embedding-3-small`, 1536 dims) and insert the document and all its chunks in one transaction. Files are identified by sha256, so re-running ingest on the same file inserts nothing and never re-embeds. Pages that produced no chunks are recorded in `documents.zero_chunk_pages`.
- **Retrieval** (`extractor/retrieve.py`): cosine distance in pgvector, top 5 with page numbers and scores, optionally restricted to one document. An HNSW index exists. At the two table sizes I checked (253 and 349 rows) the planner chose a sequential scan, and forcing it to avoid sequential scans showed the query can use the index; behaviour at larger sizes is untested.
- **Answering** (`extractor/answer.py`): retrieved chunks go to `claude-haiku-4-5-20251001` with `max_tokens=500`; the model may answer only from the labelled context and must reply exactly `not stated` when the context doesn't state the answer. Citations are parsed and checked against the retrieved `(filename, page)` pairs. On a refusal, if the searched document has pages that produced no text, the output warns that the answer may be on a page the extractor could not read.
- **Eval** (`eval/`): 15 labeled questions (10 answerable, 5 absent) against one document, graded automatically; prints answer accuracy, citation accuracy and correct-refusal rate.
- **Experimental column-aware extraction** (opt-in, see below).

## Measured results

Eval on the POL whitepaper (`python eval/run_eval.py`): **10/10 answers correct, 10/10 cited the expected page, 5/5 absent questions correctly refused.** Read this with its conditions: one run, one document (the cleanest of the four), I wrote the questions, two of the 15 questions were seen while tuning the prompt, and the SDK exposes no temperature setting so run-to-run variation is unmeasured. The raw numbers behind this and the other findings are in `docs/M4_FINDINGS.md`.

A failure the eval does not cover: on the bilingual financial report, asked *"What was HBAP's revenue in March 2026?"*, the system answered 203.513 (page 72), stated confidently and with an unsupported "(in thousands...)" unit note. 203.513 is BPI's revenue, another joint venture summarised on the same page; HBAP's actual figure is 567.618, on page 73. The cause: the chunk holding BPI's numbers ends with the heading that introduces HBAP, while the heading that names BPI sits in the previous chunk, which was not retrieved, so the model saw one entity's figures under another's name. HBAP's own revenue chunk was not in the top 5 either.

## Experimental: column-aware extraction

Bilingual reports print Indonesian and English side by side, and default extraction interleaves them line by line. `--column-aware` reads a two-column page as its left column, then its right column.

- Off by default. `python cli.py file.pdf --column-aware` (report) or `python cli.py ingest --column-aware file.pdf`.
- A page counts as two-column only if the word x-midpoints split into two clusters with an empty gutter (at least 3 pt) that no word crosses. Otherwise the default extractor runs unchanged.
- Table veto: if both sides of the gutter hold 5 or more dot-grouped amounts (e.g. `13.045.179`), the page falls back to default extraction, because splitting would put the current-year figure with one language's label and the prior-year figure with the other's.
- On the 152-page report: 75 pages get column separation, 31 are vetoed as tables, 45 fall back for no clear gutter and 1 for too few words. On the single-column whitepaper the output is byte-identical with the flag on or off.
- The extraction mode is not stored in the database. Ingestion is keyed on the file hash, so changing mode for an ingested file means deleting its document row first.

## Known issues

- Retrieval similarity does not separate answerable from absent questions: in the eval, a correct answer had a top score of 0.409 while absent questions scored up to 0.672. A similarity threshold alone cannot flag low-confidence answers.
- Wrong-entity answers: a chunk that loses its table header, or gains the next entity's heading, can be attributed to the wrong entity (the BPI/HBAP case above).
- Fixed-size chunks start mid-word and can cut numbers (4 mid-number cuts at chunk ends in the 42-page paper).
- Table detection found nothing on the financial report: `find_tables` returned 0 tables on all 15 pages I checked, including the statement of changes in equity (page 9) and the HBAP profit-or-loss summary (page 73). Tables are also never chunked separately, so table facts reach the index only as flattened text lines, and a table's header and its rows can land in different chunks.
- Some PDFs extract with words run together (the Yellow Paper has 140 of 253 chunks with a 25+ letter token); column-aware mode does not address this.
- Unresolved glyph tokens `(cid:N)` appear in 152 of 253 chunks of the Yellow Paper.
- No OCR: image-only pages are reported (`zero_chunk_pages`, plus the warning on refusals) but not read. The warning was verified on a synthetic PDF only; the only ingested page with no extractable text is page 2 of the financial report, which I did not inspect visually.
- The PDF page index and the printed page number can differ (the financial report prints `60` on PDF page 63); citations use the PDF index.
- `find_tables` (pdfplumber) produces false positives on 1x2 and 2x1 bordered regions. Not yet fixed.
- Tested on Python 3.10.11 only.

## Not built yet

- Two-signal confidence and `needs_review` (retrieval similarity plus a model-reported "explicitly stated" boolean; never a self-reported confidence number).
- Pydantic `Answer`/`Citation` models and an API.
- Automated tests.
- OCR, word-aware chunk boundaries, table-aware chunking, deployment.

## Running it

Requirements: Docker, Python 3.10+, an OpenAI API key (embeddings) and an Anthropic API key (answers).

```bash
# start Postgres + pgvector on localhost:5433
docker compose up -d

pip install -r requirements.txt
```

Create a `.env` in the project root:

```
DATABASE_URL=postgresql://postgres:postgres@localhost:5433/pdf_extractor
OPENAI_API_KEY=...
ANTHROPIC_API_KEY=...
```

The compose file publishes the database on 5433 because many Windows machines already run a native Postgres on 5432. The password defaults to `postgres` for local development and can be overridden with `POSTGRES_PASSWORD`. Files in `migrations/` run automatically only when the data volume is first created; on an existing volume, apply a new migration by piping it in, e.g. `Get-Content migrations/003_add_zero_chunk_pages.sql | docker compose exec -T db psql -U postgres -d pdf_extractor`. Do not remove the volume to "fix" it.

```bash
python cli.py file.pdf                       # extraction report (no DB, no API keys)
python cli.py file.pdf --column-aware        # same, experimental two-column reading order
python cli.py ingest file.pdf [--column-aware]
python cli.py docs                           # list ingested documents and their ids
python cli.py ask "question" [--doc ID]      # top 5 chunks with file, page and score
python cli.py answer "question" [--doc ID]   # cited answer or "not stated"
python eval/run_eval.py                      # needs the POL whitepaper ingested as document 3
```

Rough costs so far, computed from reported token counts at list prices rather than from a bill: embedding the 152-page report took 179,338 tokens, about $0.004; an answered question costs about $0.001 to $0.002.

`tests/fixtures/synthetic_scanned_page.pdf` is a synthetic PDF with an image-only page, used to check the zero-chunk warning by hand; it is a fixture, not an automated test.
