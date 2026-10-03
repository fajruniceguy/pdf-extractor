ALTER TABLE documents ADD COLUMN IF NOT EXISTS file_sha256 TEXT;

CREATE UNIQUE INDEX IF NOT EXISTS documents_file_sha256_key ON documents (file_sha256);
