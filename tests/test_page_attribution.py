"""Test page attribution on synthetic scanned document."""
from pathlib import Path

from extractor import chunk_document, extract_pdf

FIXTURE_PATH = Path(__file__).parent / "fixtures" / "synthetic_scanned_page.pdf"

# Distinctive phrases hard-coded from fixture text:
# Page 1 contains text about Zeta Protocol being a fictional token for testing.
PAGE_1_PHRASE = "fictional token used only for testing document extraction"
# Page 3 contains text about Zeta Protocol roadmap and staking layer.
PAGE_3_PHRASE = "adds a staking layer"


def test_page_attribution():
    # 1. Extract and chunk the fixture with the project's own functions.
    doc = extract_pdf(FIXTURE_PATH)
    chunks = chunk_document(doc)

    # 2. Assert every chunk's page is an int in {1, 3}.
    assert len(chunks) > 0, "Expected at least one chunk to be produced"
    for chunk in chunks:
        assert isinstance(chunk.page, int), f"Chunk page {chunk.page!r} is not an int"
        assert chunk.page in {1, 3}, f"Chunk page {chunk.page} not in {{1, 3}}"

    # 3. Assert no chunk has page 2.
    assert not any(chunk.page == 2 for chunk in chunks), "Found chunk with page == 2"

    # 4. Using a distinctive phrase from page 1 and one from page 3 that YOU choose from the fixture
    #    text (hard-coded in the test, not derived from the code's output), assert the page-1 phrase
    #    appears only in chunks with page == 1, and the page-3 phrase only in chunks with page == 3.
    page_1_chunks = [c for c in chunks if PAGE_1_PHRASE in c.content]
    assert len(page_1_chunks) > 0, f"Expected phrase {PAGE_1_PHRASE!r} to appear in chunks"
    for c in page_1_chunks:
        assert c.page == 1, f"Chunk containing page-1 phrase has page {c.page} != 1"
    for c in chunks:
        if c.page != 1:
            assert PAGE_1_PHRASE not in c.content, f"Page-1 phrase found in chunk with page {c.page}"

    page_3_chunks = [c for c in chunks if PAGE_3_PHRASE in c.content]
    assert len(page_3_chunks) > 0, f"Expected phrase {PAGE_3_PHRASE!r} to appear in chunks"
    for c in page_3_chunks:
        assert c.page == 3, f"Chunk containing page-3 phrase has page {c.page} != 3"
    for c in chunks:
        if c.page != 3:
            assert PAGE_3_PHRASE not in c.content, f"Page-3 phrase found in chunk with page {c.page}"

    # 5. Assert the set of pages with no chunks is exactly {2}.
    all_pages = {page.page for page in doc.pages}
    chunk_pages = {chunk.page for chunk in chunks}
    pages_with_no_chunks = all_pages - chunk_pages
    assert pages_with_no_chunks == {2}, f"Expected pages with no chunks to be {{2}}, got {pages_with_no_chunks}"
