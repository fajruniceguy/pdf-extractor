# Running the demo

How to start the system from a cold machine, check that it is healthy, run three example queries, and what to do when something fails. Everything here was run and timed on 2026-10-06 on Windows 10 with PowerShell, Docker Desktop and Git for Windows. Where something was not tested, it says so.

Files that go with this runbook:

- `preflight.sh`: runs every health check in section 2 and prints PASS or FAIL for each. Read-only.
- `demo_queries.txt`: the three example commands from section 3.
- `demo_backups/`: saved outputs of those commands, for section 4.

## Reference values

| Item | Value |
|---|---|
| Project folder | `D:\Avantis\The Great Reset\pdf-extractor` |
| Database | PostgreSQL 16 with pgvector, as the Docker Compose service `db`, container `pdf_extractor_db` |
| Connection from the host | host `localhost`, port `5433` (mapped to 5432 inside the container), user `postgres`, database `pdf_extractor` |
| Password | the value of `POSTGRES_PASSWORD`; docker-compose.yml supplies a development default. Not repeated here. |
| Data volume | `pdf-extractor_pgdata` (a named Docker volume; it holds all ingested data) |
| Tables | `documents(id, filename, page_count, created_at, file_sha256, zero_chunk_pages)` and `chunks(id, document_id, page_number, content, embedding vector(1536))`, with the HNSW index `chunks_embedding_hnsw_idx` |
| Variables (names only), in `.env` in the project folder | `DATABASE_URL` (database), `OPENAI_API_KEY` (embeds each question), `ANTHROPIC_API_KEY` (the answer model) |
| Python | the system Python 3.10.11 (`C:\Users\User\AppData\Local\Microsoft\WindowsApps\PythonSoftwareFoundation.Python.3.10_qbz5n2kfra8p0\python.exe`). No virtual environment exists in the project or its parent folder, so there is nothing to activate. If you keep a virtual environment somewhere else, I did not find it. |

Ingested documents (document id is what `--doc` takes):

| id | File | Pages | Chunks |
|---|---|---|---|
| 1 | Ethereum Yellow Paper | 42 | 253 |
| 2 | AC_Research_Bitget_Token_BGB.pdf | 7 | 19 |
| 3 | POL Whitepaper v0.2.pdf | 25 | 77 |
| 4 | ptba-quarterly-report.pdf (ingested with `--column-aware`) | 152 | 805 |

`.env.example` does not exist in the repository, although one error message refers to it. The three variables above go in `.env`.

## 1. Cold start

From a fresh PowerShell window, in this order:

```powershell
# 1. Go to the project folder
cd "D:\Avantis\The Great Reset\pdf-extractor"

# 2. Start Docker Desktop if it is not running, then wait until `docker info` stops printing errors
Start-Process "C:\Users\User\AppData\Local\Programs\DockerDesktop\Docker Desktop.exe"
docker info

# 3. Start the database container (reuses the existing data volume)
docker compose up -d

# 4. Wait until it reports healthy
docker inspect --format "{{.State.Health.Status}}" pdf_extractor_db

# 5. Confirm Python and the dependencies (no output after the version line means they import)
python --version
python -c "import psycopg, pgvector, openai, anthropic, dotenv, pdfplumber"

# 6. Run the health checks (Git Bash, see the warning below)
& "C:\Program Files\Git\bin\bash.exe" preflight.sh
```

Measured on 2026-10-06 from a machine with Docker Desktop closed: the Docker engine was ready about 19 s after launch and the container was healthy about 7 s later (26 s in total).

Two warnings:

- **Do not run `docker compose down -v` or remove the volume.** That deletes every ingested document and embedding. Re-ingesting means paying for embeddings again.
- **In PowerShell, plain `bash` is not Git Bash.** On this machine it resolves to `C:\Windows\system32\bash.exe`, the WSL launcher. Use the full Git Bash path shown in step 6, or open a Git Bash terminal and run `bash preflight.sh`.

## 2. Health checks

One command runs all of them:

```powershell
& "C:\Program Files\Git\bin\bash.exe" preflight.sh            # includes one real answer, about $0.0015
& "C:\Program Files\Git\bin\bash.exe" preflight.sh --no-llm   # skips the answer call
```

It took 17 to 25 s in full runs (the final answer check alone took 11 to 17 s). A healthy run, as saved in `demo_backups/00_preflight.txt`:

```
[PASS] Docker engine is reachable
[PASS] Container pdf_extractor_db is healthy (host port mapping: 0.0.0.0:5433 [::]:5433 )
[PASS] Database answers a query inside the container (user postgres, database pdf_extractor)
[PASS] Python dependencies import (Python 3.10.11)
[PASS] DATABASE_URL, OPENAI_API_KEY and ANTHROPIC_API_KEY are all set (values not shown)
[PASS] The application connects through DATABASE_URL
[PASS] Four documents are ingested, each with chunks
         document 1: 253 chunks  (Ethereum Yellow Paper_ a formal specification of Ethereum, a programmable blockchain.pdf)
         document 2: 19 chunks  (AC_Research_Bitget_Token_BGB.pdf)
         document 3: 77 chunks  (POL Whitepaper v0.2.pdf)
         document 4: 805 chunks  (ptba-quarterly-report.pdf)
[PASS] Chunk counts match the recorded values (1:253 2:19 3:77 4:805)
[PASS] No chunk is missing an embedding (vector dimension 1536)
[PASS] Answer works end to end: stated with a page-9 citation (11 s)

10 passed, 0 failed
```

The script never writes to the database (every statement is a `SELECT`) and never prints the keys or the password. Its failure paths were tested with dummy values: an empty `ANTHROPIC_API_KEY` is reported by name, and an unreachable database is reported after at most 25 s and makes the final test query skip instead of hang.

Manual equivalents, if the script cannot run:

```powershell
# Database up and healthy
docker ps --format "{{.Names}}: {{.Status}} | {{.Ports}}"

# All four documents with chunk counts (expect 253, 19, 77, 805)
docker exec pdf_extractor_db psql -U postgres -d pdf_extractor -c "SELECT d.id, d.filename, count(c.id) AS chunks FROM documents d LEFT JOIN chunks c ON c.document_id = d.id GROUP BY d.id ORDER BY d.id;"

# Chunks without an embedding (expect 0)
docker exec pdf_extractor_db psql -U postgres -d pdf_extractor -c "SELECT count(*) FROM chunks WHERE embedding IS NULL;"

# Keys are set, without printing them (expect True three times)
python -c "import os; from dotenv import load_dotenv; load_dotenv('.env'); print({n: bool(os.environ.get(n)) for n in ('DATABASE_URL','OPENAI_API_KEY','ANTHROPIC_API_KEY')})"

# A test query through the application
python cli.py docs
```

## 3. Demo script

Three queries, also in `demo_queries.txt`. Each makes real API calls (one embedding, one answer) and costs about $0.0013 to $0.0018.

**1. A question the system answers, with a citation**

```powershell
python cli.py answer "For how many years can the POL emission rate not be changed?" --doc 3
```

Expected: the answer is 10 years, cited as `[POL Whitepaper v0.2.pdf, page 10]`; `Stated: True`; top retrieval score about 0.573. Took 7.3 s (1011 tokens in, 69 out). This question was correct with the expected page cited in all three saved eval re-runs (`eval/results_run1.json` to `results_run3.json`). Saved: `demo_backups/01_pol_answered.txt`.

**2. A question whose answer is not in the document**

```powershell
python cli.py answer "What block time do Polygon chains use?" --doc 3
```

Expected: `Answer: not stated`, `Stated: False`, `Citations: none`. The top retrieval score is still 0.655, so the search finds related text (page 14 says block time is configurable) but the document gives no value. Took 5.6 s. Saved: `demo_backups/02_pol_not_stated.txt`.

The model does not always answer with exactly `not stated`. Across the nine runs I could see for this question (three saved eval re-runs and six live runs on 2026-10-06), 8 returned exactly that and 1 appended an explanatory sentence. The command still reports `Stated: False` and prints a `WARNING:` line saying the extra text is not part of the answer. That output is saved in `demo_backups/02b_pol_not_stated_with_extra_text.txt`.

**3. A known failure: the wrong entity's figure**

```powershell
python cli.py answer "What was HBAP's revenue for the period ended March 31, 2026?" --doc 4
```

Expected: the answer is `203.513`, cited to page 72. That is the revenue of a different company in the same report (BPI); HBAP's revenue is 567.618, on page 73. All three saved runs gave 203.513 (two of them start with "According to the context,"). The cause is documented in `README.md` and in `docs/M4_FINDINGS.md`, section 10: the chunk holding BPI's numbers ends with the heading that introduces HBAP. Saved: `demo_backups/03_ptba_hbap_run1.txt`, `run2`, `run3`.

Timings of the saved runs:

| Query | Time |
|---|---|
| 1. POL answered | 7.3 s |
| 2. POL not stated | 5.6 s (a second run, the one with extra text, took 5.9 s) |
| 3. HBAP run 1 / run 2 / run 3 | 5.8 s / 16.2 s / 6.2 s |

Typical is 6 to 7 s. The slowest I saw was 16 s in a saved run and 22 s in a failure test. The command has no timeout of its own; if nothing has printed after about a minute, press Ctrl+C and use section 4.

## 4. Fallback: saved outputs

If a live query fails, show the saved output instead and say it is a saved output from an earlier run, not a live one.

```powershell
Get-Content demo_backups\00_preflight.txt
Get-Content demo_backups\01_pol_answered.txt
Get-Content demo_backups\02_pol_not_stated.txt
Get-Content demo_backups\02b_pol_not_stated_with_extra_text.txt
Get-Content demo_backups\03_ptba_hbap_run1.txt
```

In Git Bash the same files work with `cat`. Each file starts with a header (when it was saved, exit code, duration, and the exact command) and then the raw output. They are real outputs from 2026-10-06 against the live database. Answer wording can differ from run to run (the SDK exposes no temperature setting); in the saved POL eval re-runs the stated flags, cited pages and grades were identical every time.

## 5. Troubleshooting

| Symptom | Likely cause | Fix |
|---|---|---|
| A command prints nothing for more than about 10 s | Postgres is unreachable. I saw `python cli.py docs` block for over 60 s with no error when nothing was listening on the database port (tested on unused ports 5998 and 5999, not with the real container stopped). | Ctrl+C. Run `docker ps`. If the container is missing or stopped, run `docker compose up -d` and wait until it is healthy. |
| `failed to connect to the docker API at npipe:////./pipe/dockerDesktopLinuxEngine` | Docker Desktop is not running. | Start it (section 1, step 2) and wait about 20 s. |
| `docker ps` does not list `pdf_extractor_db`, or it is not healthy | The container is stopped or still starting. | `docker compose up -d`, wait about 10 s. If still unhealthy: `docker logs pdf_extractor_db --tail 20`. Do not use `-v`. |
| Docker cannot start the container because the port is in use | Something else listens on 5433. | `Get-NetTCPConnection -LocalPort 5433 -State Listen`, find the process by its `OwningProcess` id, and stop it. Changing the port would mean editing `docker-compose.yml` and `DATABASE_URL`, which is not part of this runbook. |
| `password authentication failed for user "postgres"` | `DATABASE_URL` points at port 5432, where a native Windows PostgreSQL 18 service (`postgresql-x64-18`) listens, instead of the container on 5433. This happened on 2026-10-03. | Make sure `DATABASE_URL` uses port 5433. |
| `ModuleNotFoundError: No module named 'psycopg'` (or `openai`, `anthropic`, `dotenv`) | The `python` on PATH is not the one with the dependencies. There is no project virtual environment. | `python -c "import sys; print(sys.executable)"` should print the WindowsApps Python from the reference table. If a virtual environment is active and lacks the packages, deactivate it or run `pip install -r requirements.txt`. |
| `bash preflight.sh` fails oddly or cannot find `docker` or `python` | Plain `bash` in PowerShell is the WSL launcher. | Use `& "C:\Program Files\Git\bin\bash.exe" preflight.sh`, or a Git Bash terminal. |
| `error: ANTHROPIC_API_KEY is not set (see .env.example)` | The variable is missing or empty. (`.env.example` does not exist; set it in `.env`.) | Add `ANTHROPIC_API_KEY` to `.env`. Tested with an empty value. |
| `error: Anthropic API error: Error code: 401 ... API key is invalid.` | The Anthropic key is wrong. | Correct the key in `.env`. Tested with a dummy key. |
| A long traceback ending in `openai.AuthenticationError: Error code: 401 ... Incorrect API key provided` | The OpenAI key is wrong. The last line is the one that matters. | Correct `OPENAI_API_KEY` in `.env`. Tested with a dummy key. |
| API rate limit or out of credits | Not tested. From the code: both SDK clients retry transient rate-limit and server errors twice. After that, an Anthropic failure prints `error: Anthropic API error: ...`, and an OpenAI failure prints a traceback ending in an `openai.` error. The exact text for an exhausted balance is unverified. | Check the provider's billing page, wait if it is a rate limit, and use section 4 meanwhile. |
| Special characters in the output appear as `?` | The console cannot encode them; the command replaces them. | Not an error. |

Avoid during a demo:

- `docker compose down -v` or anything that removes the volume.
- `python cli.py ingest ...` on a new file. It embeds the whole file and costs money. Ingesting a file that is already stored only prints `already ingested`.
- Editing `.env`, `docker-compose.yml` or any file under `extractor/`.
