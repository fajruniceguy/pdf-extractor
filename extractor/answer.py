"""Answer layer: retrieved chunks -> Claude Haiku -> a cited answer or "not stated"."""
from __future__ import annotations

import os
import re
from dataclasses import dataclass

import anthropic
from dotenv import load_dotenv

from .db import connect
from .retrieve import SearchResult, search

MODEL = "claude-haiku-4-5-20251001"
MAX_TOKENS = 500
MAX_RETRIES = 2  # SDK retries transient 429/5xx this many times, then raises
INPUT_USD_PER_MTOK = 1.00
OUTPUT_USD_PER_MTOK = 5.00

SYSTEM_PROMPT = """You answer questions using ONLY the context excerpts in the user message. \
Each excerpt is labelled with its filename and page number, like [report.pdf, page 9].

Rules:
1. Use only the provided context. Never use outside knowledge about any topic in the context, \
even if you are confident you know the answer.
2. If the context does not state the answer, reply with exactly: not stated
3. If the context does not state the answer, your entire reply must be exactly: not stated \
— with no explanation, no preamble, and no trailing sentence.
4. Partial information is not an answer. If the context discusses the topic but does not give \
the specific value or fact asked for, reply with exactly: not stated
5. Cite the filename and page number for every claim, in the form [filename, page N], placed \
right after the claim. Cite only filename and page combinations that appear in the context labels.
6. Keep answers short and factual."""

# Filenames can contain commas, so anchor on the trailing ", page N]".
_CITATION = re.compile(r"\[([^\[\]]+?),\s*page\s+(\d+)\]", re.IGNORECASE)


@dataclass(frozen=True)
class AnswerResult:
    question: str
    answer: str
    stated: bool
    citations: list[tuple[str, int]]  # (filename, page); empty for a refusal
    unsupported_citations: list[tuple[str, int]]  # cited but not in the retrieved context
    note: str | None  # any text the model added after "not stated"
    unreadable_pages_warning: str | None  # refusals only: pages the extractor got no text from
    retrieved: list[SearchResult]
    raw_output: str
    stop_reason: str
    input_tokens: int
    output_tokens: int
    cost_usd: float


def _format_context(results: list[SearchResult]) -> str:
    return "\n\n".join(f"[{r.filename}, page {r.page_number}] {r.content}" for r in results)


def _unreadable_pages_warning(document_id: int | None) -> str | None:
    """Warning text for documents in scope that have pages with no extractable text."""
    with connect() as conn:
        rows = conn.execute(
            "SELECT filename, zero_chunk_pages FROM documents "
            "WHERE cardinality(zero_chunk_pages) > 0 AND (%(doc)s::int IS NULL OR id = %(doc)s) "
            "ORDER BY id",
            {"doc": document_id},
        ).fetchall()
    sentences = []
    for filename, pages in rows:
        label = "Page" if len(pages) == 1 else "Pages"
        sentences.append(
            f"{label} {', '.join(str(p) for p in pages)} of {filename} produced no extractable text."
        )
    if not sentences:
        return None
    return " ".join(sentences) + " The answer may be present on a page the extractor could not read."


def answer(question: str, document_id: int | None = None, k: int = 5) -> AnswerResult:
    results = search(question, k=k, document_id=document_id)

    load_dotenv()
    if not os.environ.get("ANTHROPIC_API_KEY"):
        raise RuntimeError("ANTHROPIC_API_KEY is not set (see .env.example)")
    client = anthropic.Anthropic(max_retries=MAX_RETRIES)

    try:
        response = client.messages.create(
            model=MODEL,
            max_tokens=MAX_TOKENS,
            system=SYSTEM_PROMPT,
            messages=[
                {
                    "role": "user",
                    "content": f"Context:\n\n{_format_context(results)}\n\nQuestion: {question}",
                }
            ],
        )
    except anthropic.APIError as e:
        raise RuntimeError(f"Anthropic API error: {e}") from e

    raw = "".join(block.text for block in response.content if block.type == "text")
    text = raw.strip()
    first_line, _, rest = text.partition("\n")

    if first_line.strip().lower().rstrip(".") == "not stated":
        stated = False
        text = "not stated"
        note = rest.strip() or None
        warning = _unreadable_pages_warning(document_id)
        cited: list[tuple[str, int]] = []
        unsupported: list[tuple[str, int]] = []
    else:
        stated = True
        note = None
        warning = None
        cited = sorted({(name.strip(), int(page)) for name, page in _CITATION.findall(text)})
        context_labels = {(r.filename, r.page_number) for r in results}
        unsupported = [c for c in cited if c not in context_labels]
    usage = response.usage
    cost = (
        usage.input_tokens * INPUT_USD_PER_MTOK + usage.output_tokens * OUTPUT_USD_PER_MTOK
    ) / 1_000_000

    return AnswerResult(
        question=question,
        answer=text,
        stated=stated,
        citations=cited,
        unsupported_citations=unsupported,
        note=note,
        unreadable_pages_warning=warning,
        retrieved=results,
        raw_output=raw,
        stop_reason=response.stop_reason,
        input_tokens=usage.input_tokens,
        output_tokens=usage.output_tokens,
        cost_usd=cost,
    )
