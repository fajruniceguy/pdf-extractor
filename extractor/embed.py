"""Embeddings via OpenAI text-embedding-3-small, in batches."""
from __future__ import annotations

from dotenv import load_dotenv
from openai import OpenAI

EMBEDDING_MODEL = "text-embedding-3-small"
EMBEDDING_DIM = 1536  # must match chunks.embedding vector(1536)
BATCH_SIZE = 100
MAX_RETRIES = 2  # SDK retries transient 429/5xx this many times, then raises


def embed_texts(texts: list[str], client: OpenAI | None = None) -> tuple[list[list[float]], int]:
    """Return (vectors in input order, total tokens used)."""
    if client is None:
        load_dotenv()
        client = OpenAI(max_retries=MAX_RETRIES)

    vectors: list[list[float]] = []
    tokens = 0
    for start in range(0, len(texts), BATCH_SIZE):
        batch = texts[start : start + BATCH_SIZE]
        response = client.embeddings.create(model=EMBEDDING_MODEL, input=batch)
        data = sorted(response.data, key=lambda item: item.index)
        if len(data) != len(batch):
            raise RuntimeError(f"expected {len(batch)} embeddings, got {len(data)}")
        for item in data:
            if len(item.embedding) != EMBEDDING_DIM:
                raise RuntimeError(
                    f"expected {EMBEDDING_DIM}-dim embedding, got {len(item.embedding)}"
                )
            vectors.append(item.embedding)
        tokens += response.usage.total_tokens
    return vectors, tokens
