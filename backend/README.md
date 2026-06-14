# LlamaIndex AI Document Intelligence Platform — Backend

A SaaS-style document intelligence backend built with **FastAPI** and **LlamaIndex**.
Upload PDF / TXT / DOCX documents, index them with OpenAI embeddings into a
persistent on-disk LlamaIndex vector store, and then:

- 💬 **Chat (RAG)** over your documents with **source citations**
- 🧾 **Extract structured fields** (people, dates, amounts, obligations, risks, …)
- 📝 **Summarize** documents
- 🔍 **Compare** two documents
- 📊 **Generate** a markdown intelligence report

---

## Architecture

```
backend/
  app/
    main.py                 # FastAPI app, routers, lifespan, error handling
    config.py               # Env-driven settings (pydantic-settings)
    routes/                 # health, documents, chat, extraction, reports
    services/
      llamaindex_service.py # Indexing + RAG (LlamaIndex local store, OpenAI)
      document_service.py   # File storage, text extraction, DB CRUD
      extraction_service.py # Structured extraction / summarize / compare
      report_service.py     # Markdown report builder
    db/                     # SQLAlchemy engine + Document model (SQLite)
    schemas/                # Pydantic request/response models
    utils/logger.py         # Logging config
  data/
    uploads/                # Stored original files
    index_storage/          # Persisted LlamaIndex vector index (JSON)
    app.db                  # SQLite metadata (auto-created)
  tests/                    # Offline pytest suite (AI calls monkeypatched)
```

- **Metadata** (filenames, sizes, status, chunk counts) → SQLite.
- **Vectors** → LlamaIndex `SimpleVectorStore` persisted on disk as JSON; each
  chunk tagged with `document_id` + `filename` so retrieval can be filtered and
  answers cited. (Swap in Chroma/Qdrant/pgvector for production scale.)
- **Original files** → `data/uploads/`.

---

## Prerequisites

- Python **3.10+** (tested on 3.12)
- An **OpenAI API key**

---

## Setup (Windows / PowerShell)

```powershell
cd C:\MY_Projects\llamaindex-document-agent\backend

# 1. Create & activate a virtual environment
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# 2. Install dependencies
python -m pip install --upgrade pip
pip install -r requirements.txt

# 3. Configure environment
copy .env.example .env
#   then edit .env and set OPENAI_API_KEY=sk-...
```

### Setup (macOS / Linux)

```bash
cd /path/to/llamaindex-document-agent/backend
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
cp .env.example .env   # then edit .env
```

---

## Run the backend locally

```powershell
# from backend/ with the venv active
uvicorn app.main:app --reload --port 8000
```

- API root: http://localhost:8000/
- Interactive docs (Swagger): http://localhost:8000/docs
- Health: http://localhost:8000/health

---

## API Endpoints

| Method | Path                  | Description                                  |
|--------|-----------------------|----------------------------------------------|
| GET    | `/health`             | Service health + config status               |
| POST   | `/documents/upload`   | Upload & index a PDF/TXT/DOCX (`file` field)  |
| GET    | `/documents`          | List all documents                           |
| GET    | `/documents/{id}`     | Get one document's metadata                   |
| POST   | `/chat`               | RAG question answering with source citations |
| POST   | `/extract`            | Structured field extraction                  |
| POST   | `/summarize`          | Summarize a document                         |
| POST   | `/compare`            | Compare two documents                        |
| POST   | `/generate-report`    | Markdown intelligence report                 |
| GET    | `/usage`              | The calling key's own usage counters         |
| GET    | `/auth/usage`         | Usage across all keys (`X-Admin-Token`)      |

### Example requests

Upload:

```powershell
curl.exe -X POST http://localhost:8000/documents/upload -F "file=@C:\path\to\contract.pdf"
```

Chat (RAG with citations):

```powershell
curl.exe -X POST http://localhost:8000/chat `
  -H "Content-Type: application/json" `
  -d '{"question":"What are the payment terms?"}'
```

Response shape:

```json
{
  "answer": "The payment terms are ...",
  "sources": [
    {"document_id": "…", "filename": "contract.pdf", "snippet": "…", "score": 0.87}
  ]
}
```

Extract structured fields:

```powershell
curl.exe -X POST http://localhost:8000/extract `
  -H "Content-Type: application/json" `
  -d '{"document_id":"<id>"}'
```

Returns: `document_type, title, key_people, key_dates, prices_or_amounts,
obligations, risks, action_items, summary`.

Compare two documents:

```powershell
curl.exe -X POST http://localhost:8000/compare `
  -H "Content-Type: application/json" `
  -d '{"document_id_a":"<id1>","document_id_b":"<id2>","focus":"pricing"}'
```

Generate a report:

```powershell
curl.exe -X POST http://localhost:8000/generate-report `
  -H "Content-Type: application/json" `
  -d '{"document_id":"<id>"}'
```

---

## Authentication (API keys)

When `AUTH_ENABLED=true` (default), all data/AI endpoints require an
`X-API-Key` header. `/health` and `/` stay public. There are two ways to
authenticate:

1. **Static keys** — set `API_KEYS` to one or more comma-separated keys for
   instant access (great for local dev / a single client).
2. **Managed keys** — set `ADMIN_API_TOKEN` to unlock the `/auth` key-management
   API. Keys are stored hashed (SHA-256); the plaintext is shown only once.

| Method | Path              | Auth            | Description                |
|--------|-------------------|-----------------|----------------------------|
| POST   | `/auth/keys`      | `X-Admin-Token` | Mint a key (returns secret once) |
| GET    | `/auth/keys`      | `X-Admin-Token` | List keys (metadata only)  |
| DELETE | `/auth/keys/{id}` | `X-Admin-Token` | Revoke a key               |

```powershell
# Mint a key (needs ADMIN_API_TOKEN set on the server)
curl.exe -X POST http://localhost:8000/auth/keys `
  -H "X-Admin-Token: <your-admin-token>" `
  -H "Content-Type: application/json" `
  -d '{"name":"my-client"}'
# -> { "id": "...", "prefix": "dia_xxxxxx", "api_key": "dia_....", ... }

# Use the key on a protected endpoint
curl.exe http://localhost:8000/documents -H "X-API-Key: dia_...."
```

Missing/invalid key → `401`. Calling `/auth/*` without `ADMIN_API_TOKEN`
configured → `403`. To disable auth entirely (e.g. quick local testing), set
`AUTH_ENABLED=false`.

### Per-key document ownership

Each API key owns its own documents. Every uploaded document is stamped with an
**owner id** derived from the calling key, and that id is also stored on every
indexed chunk:

- managed (DB) key → the key's id
- static key       → `static:<sha256-prefix>` (each static key is isolated)
- auth disabled    → `public` (single shared space)

All operations are scoped to the caller:

- `GET /documents` lists **only** the caller's documents.
- `GET /documents/{id}`, `extract`, `summarize`, `compare`, `generate-report`
  return `404` for a document owned by a different key (existence is not leaked).
- `POST /chat` retrieval is filtered to the caller's chunks; passing another
  key's `document_ids` returns `404`.

> Upgrading an existing index from before this change? Re-upload documents so
> their chunks carry the `owner_id` metadata used for retrieval scoping.

### Usage tracking

Every request to a protected endpoint is recorded against the caller's owner id
in a `usage_stats` table: a `total_requests` counter plus per-operation counters
(`uploads`, `chats`, `extractions`, `summaries`, `comparisons`, `reports`).
Counts reflect received requests (recorded before the handler runs, so failed
operations still count).

- `GET /usage` — the calling key's own counters + live `document_count`.
- `GET /auth/usage` (admin) — counters for every owner, with managed-key labels.

```powershell
curl.exe http://localhost:8000/usage -H "X-API-Key: dia_...."
curl.exe http://localhost:8000/auth/usage -H "X-Admin-Token: <your-admin-token>"
```

## Tests

The test suite runs **fully offline** — all OpenAI/LlamaIndex calls are
monkeypatched, so no API key or network access is required.

```powershell
# from backend/ with the venv active
pytest
```

---

## Configuration reference

All settings are read from environment variables / `.env` (see `.env.example`):

| Variable                  | Default                       | Description                          |
|---------------------------|-------------------------------|--------------------------------------|
| `OPENAI_API_KEY`          | _(empty)_                     | Required for AI endpoints            |
| `AUTH_ENABLED`            | `true`                        | Require `X-API-Key` on data/AI routes|
| `API_KEYS`                | _(empty)_                     | Comma-separated static API keys      |
| `ADMIN_API_TOKEN`         | _(empty)_                     | Unlocks the `/auth` management API   |
| `OPENAI_MODEL`            | `gpt-4o-mini`                 | Chat/extraction LLM                  |
| `OPENAI_EMBEDDING_MODEL`  | `text-embedding-3-small`      | Embedding model                      |
| `CHUNK_SIZE`              | `1024`                        | Chunk size for indexing              |
| `CHUNK_OVERLAP`           | `128`                         | Chunk overlap                        |
| `SIMILARITY_TOP_K`        | `4`                           | Chunks retrieved per query           |
| `MAX_EXTRACT_CHARS`       | `24000`                       | Max chars sent to LLM per request    |
| `MAX_UPLOAD_MB`           | `25`                          | Max upload size                      |
| `CORS_ORIGINS`            | `*`                           | Comma-separated allowed origins      |
| `DATA_DIR`                | `backend/data`                | Override storage location            |

---

## Notes & limitations (Phase 1 MVP)

- AI endpoints return **HTTP 503** until `OPENAI_API_KEY` is configured.
- No authentication yet (single-tenant local MVP).
- Extraction/summarization truncate very long documents to `MAX_EXTRACT_CHARS`.
- The vector index and SQLite DB persist across restarts under `data/`.
```
