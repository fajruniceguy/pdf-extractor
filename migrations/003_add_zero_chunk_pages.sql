-- Pages of a document that produced no chunks (no extractable text, e.g. scanned pages).
-- NULL = not computed yet; '{}' = computed, every page produced at least one chunk.
ALTER TABLE documents ADD COLUMN IF NOT EXISTS zero_chunk_pages INT[];
