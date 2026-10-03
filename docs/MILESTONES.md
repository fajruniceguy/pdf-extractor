# Milestones

Work only on the milestone named in the current session. Don't build ahead.

## MUST (before Wednesday 14.00)

**M1. Ingestion writes to the database.**
Embed chunks, then insert documents and chunks into Postgres.
Done when: `SELECT count(*) FROM chunks WHERE embedding IS NOT NULL` returns > 0, every row has
a page_number, and re-running ingest on the same file inserts nothing new.

**M2. Retrieval returns cited chunks.**
Embed a question, run cosine similarity against pgvector, and return the top 5 with page numbers and scores.
Done when: a CLI command takes a question and prints five chunks, each with page and score.

**M3. Answer layer with citations and "not stated".**
Send retrieved chunks to claude-haiku-4-5-20251001 and answer only from that context. Return
"not stated" when the answer is absent. Cap max_tokens at 500.
Done when: one command (PDF in, question in) prints an answer with page citations, AND a
deliberately absent-answer question returns "not stated" rather than a guess.

**M4. Run on a real document.**
One genuine PDF of 20+ pages.
Done when: M1–M3 pass on it, and what broke is written down in docs/M4_FINDINGS.md.

**M5. Fix the CV.** (Human task, no code.)
Done when: every CV line describes something that can be screen-shared.

## SHOULD (only if all MUSTs are done by Tuesday afternoon)

**S1. Minimal eval.** 15 questions, 5 of them with answers absent from the document.
Report answer accuracy, citation accuracy, and correct-refusal rate.
Done when: a script prints those three numbers.

**S2. Two-signal confidence.** needs_review fires on low retrieval similarity OR when the model
reports the answer was inferred rather than explicitly stated. Never use model self-reported
confidence scores.
Done when: low-confidence answers are flagged in the output.

**S3. One real test.** Assert that every chunk carries the correct page on a 3-page fixture.
Done when: `pytest` passes.

## Out of scope until after the interview
FastAPI, Pydantic API models, word-aware chunk boundaries, tables flowing into chunks,
the find_tables false-positive fix, OCR, deployment.

## Hard rule
Code freeze is Tuesday 18.00. No new code after that.
