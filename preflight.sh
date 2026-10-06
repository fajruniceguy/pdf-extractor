#!/usr/bin/env bash
# Read-only health checks for the demo. Prints PASS or FAIL per check and never prints secret values.
#
#   bash preflight.sh            full check, including one real answer (costs about $0.002)
#   bash preflight.sh --no-llm   skip the answer call; only embed one question and search
#
# Run it in Git Bash. In PowerShell, plain `bash` is the WSL launcher, so use:
#   & "C:\Program Files\Git\bin\bash.exe" preflight.sh
#
# Nothing here writes to the database: every SQL statement is a SELECT, and the test
# query only reads.

cd "$(dirname "${BASH_SOURCE[0]}")" || exit 2
export MSYS_NO_PATHCONV=1

CONTAINER="pdf_extractor_db"
DB_USER="postgres"
DB_NAME="pdf_extractor"
NO_LLM=0
[ "${1:-}" = "--no-llm" ] && NO_LLM=1

# Counts recorded when the four documents were ingested (document id, chunks).
EXPECTED_COUNTS="1:253 2:19 3:77 4:805"

pass=0
fail=0
ok()  { printf '[PASS] %s\n' "$1"; pass=$((pass + 1)); }
bad() { printf '[FAIL] %s\n' "$1"; [ -n "${2:-}" ] && printf '       hint: %s\n' "$2"; fail=$((fail + 1)); }
psql_q() { timeout 30 docker exec "$CONTAINER" psql -U "$DB_USER" -d "$DB_NAME" -tA -c "$1" 2>/dev/null; }

echo "Preflight $(date '+%Y-%m-%d %H:%M:%S')  (project: $(pwd))"
echo

# 1. Docker engine
if timeout 20 docker info >/dev/null 2>&1; then
  ok "Docker engine is reachable"
else
  bad "Docker engine is not reachable" "start Docker Desktop and wait until it reports it is running"
fi

# 2. Database container
health=$(timeout 20 docker inspect -f '{{.State.Health.Status}}' "$CONTAINER" 2>/dev/null)
ports=$(timeout 20 docker port "$CONTAINER" 5432/tcp 2>/dev/null | tr '\n' ' ')
if [ "$health" = "healthy" ]; then
  ok "Container $CONTAINER is healthy (host port mapping: ${ports:-none})"
else
  bad "Container $CONTAINER is not healthy (status: ${health:-not found})" "run: docker compose up -d   (from the project folder), then wait ~10 s"
fi
case "$ports" in *:5433*) ;; *) [ "$health" = "healthy" ] && bad "Port 5433 is not published for $CONTAINER" "check docker-compose.yml and docker ps";; esac

# 3. Query through the container
if [ "$(psql_q 'SELECT 1')" = "1" ]; then
  ok "Database answers a query inside the container (user $DB_USER, database $DB_NAME)"
else
  bad "Database did not answer a query inside the container" "docker logs $CONTAINER --tail 20"
fi

# 4. Python and dependencies (no virtualenv is used; this is the interpreter on PATH)
pyver=$(python --version 2>&1)
if python -c "import psycopg, pgvector, openai, anthropic, dotenv, pdfplumber" >/dev/null 2>&1; then
  ok "Python dependencies import ($pyver)"
else
  bad "Python dependencies are missing or Python is not on PATH ($pyver)" "pip install -r requirements.txt"
fi

# 5. Variables, checked the way the app sees them (shell environment first, then .env). Names only.
missing=$(python - <<'EOF' 2>/dev/null
import os
from dotenv import load_dotenv
load_dotenv(".env")
print(" ".join(n for n in ("DATABASE_URL", "OPENAI_API_KEY", "ANTHROPIC_API_KEY") if not os.environ.get(n)))
EOF
)
if [ $? -ne 0 ]; then
  bad "Could not check the environment variables" "check that python-dotenv is installed"
elif [ -z "$missing" ]; then
  ok "DATABASE_URL, OPENAI_API_KEY and ANTHROPIC_API_KEY are all set (values not shown)"
else
  bad "Not set: $missing" "add them to .env in the project folder (variable names only are shown here)"
fi

# 6. The application's own database path (DATABASE_URL, host port 5433)
app_db_ok=0
if [ "$(timeout 25 python -c "from extractor.db import connect; print(connect().execute('SELECT 1').fetchone()[0])" 2>/dev/null)" = "1" ]; then
  app_db_ok=1
  ok "The application connects through DATABASE_URL"
else
  bad "The application could not connect through DATABASE_URL (it can hang when Postgres is unreachable; this check gives up after 25 s)" "confirm the container is healthy, then check the port in DATABASE_URL is 5433"
fi

# 7. Documents and chunk counts
rows=$(psql_q "SELECT d.id || '|' || count(c.id) || '|' || d.filename FROM documents d LEFT JOIN chunks c ON c.document_id = d.id GROUP BY d.id, d.filename ORDER BY d.id")
ndocs=$(printf '%s\n' "$rows" | grep -c '|')
if [ "$ndocs" -eq 4 ] && ! printf '%s\n' "$rows" | grep -q '^[0-9]*|0|'; then
  ok "Four documents are ingested, each with chunks"
else
  bad "Expected four ingested documents with chunks; found $ndocs" "run: python cli.py docs"
fi
printf '%s\n' "$rows" | while IFS='|' read -r id n name; do [ -n "$id" ] && printf '         document %s: %s chunks  (%s)\n' "$id" "$n" "$name"; done

# 8. Counts match the values recorded at ingest time
mismatch=""
for pair in $EXPECTED_COUNTS; do
  id=${pair%%:*}; want=${pair##*:}
  got=$(printf '%s\n' "$rows" | awk -F'|' -v id="$id" '$1 == id {print $2}')
  [ "$got" = "$want" ] || mismatch="$mismatch doc$id=${got:-none}(recorded $want)"
done
if [ -z "$mismatch" ]; then
  ok "Chunk counts match the recorded values ($EXPECTED_COUNTS)"
else
  bad "Chunk counts differ from the recorded values:$mismatch" "something was ingested or deleted since the counts were recorded"
fi

# 9. Embeddings
nulls=$(psql_q "SELECT count(*) FROM chunks WHERE embedding IS NULL")
dims=$(psql_q "SELECT string_agg(DISTINCT vector_dims(embedding)::text, ',') FROM chunks")
if [ "$nulls" = "0" ] && [ "$dims" = "1536" ]; then
  ok "No chunk is missing an embedding (vector dimension $dims)"
else
  bad "Embedding check failed (chunks without embedding: ${nulls:-?}, dimensions: ${dims:-?})" "do not re-ingest during the demo; use the saved outputs in demo_backups/"
fi

# 10. A real test query
start=$SECONDS
if [ "$app_db_ok" -ne 1 ]; then
  bad "Test query skipped: the application cannot reach the database (see the check above)"
elif [ "$NO_LLM" -eq 1 ]; then
  out=$(timeout 90 python cli.py ask "What is the initial supply of POL?" --doc 3 2>&1)
  if printf '%s' "$out" | head -1 | grep -q 'page 9'; then
    ok "Search works: the top result for the test question is on page 9 ($((SECONDS - start)) s, no answer call)"
  else
    bad "Search test failed" "run the ask command by hand and read the error"
  fi
else
  out=$(timeout 90 python cli.py answer "What is the initial supply of POL?" --doc 3 2>&1)
  if printf '%s' "$out" | grep -q '^Stated:   True' && printf '%s' "$out" | grep -q 'Citations: .*page 9'; then
    ok "Answer works end to end: stated with a page-9 citation ($((SECONDS - start)) s)"
  else
    bad "Answer test failed" "run the answer command by hand: python cli.py answer \"What is the initial supply of POL?\" --doc 3"
    printf '%s\n' "$out" | tail -3 | cut -c1-200 | sed 's/^/         /'
  fi
fi

echo
echo "$pass passed, $fail failed"
[ "$fail" -eq 0 ]
