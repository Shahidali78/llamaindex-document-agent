# LlamaIndex AI Document Intelligence Platform

A SaaS-style document intelligence platform built with **LlamaIndex**. Upload
documents, index them, then chat over them with RAG (answers cite their
sources), extract structured fields, summarize, compare documents, and generate
reports.

```
┌─────────────────────────┐        ┌──────────────────────────────┐
│  Frontend (React + Vite)│  HTTP  │  Backend (FastAPI + LlamaIndex)│
│  http://localhost:5173  │ ─────▶ │  http://localhost:8000         │
└─────────────────────────┘        │   • OpenAI LLM + embeddings    │
                                    │   • Local vector index (JSON)  │
                                    │   • SQLite metadata            │
                                    └──────────────────────────────┘
```

| Layer | Stack |
|-------|-------|
| **Backend** | Python · FastAPI · LlamaIndex · OpenAI · SQLite · local vector store |
| **Frontend** | React 18 · TypeScript · Vite 6 · Tailwind CSS v4 |
| **Infra** | Docker · docker compose · GitHub Actions CI |

> Full details live in [`backend/README.md`](backend/README.md) and
> [`frontend/README.md`](frontend/README.md).

---

## Features

- 📄 Upload **PDF / TXT / DOCX**, stored locally with metadata in SQLite
- 🔎 Parse → chunk → embed → **persist** a vector index on disk
- 💬 **Chat (RAG)** with **source citations** (filename + snippet + score)
- 🧾 **Structured extraction**: document type, title, key people, key dates,
  prices/amounts, obligations, risks, action items, summary
- 📝 **Summarize** in multiple styles
- 🔍 **Compare** two documents
- 📊 **Generate** a downloadable Markdown intelligence report
- ❤️ Health endpoint, logging, clean error handling, tests

---

## Quickstart

### Option A — Docker (both services together)

Requires Docker Desktop.

```bash
cp .env.example .env          # then set OPENAI_API_KEY
docker compose up --build
```

- Frontend → http://localhost:5173
- Backend  → http://localhost:8000  (Swagger docs at `/docs`)

### Option B — Run locally (two terminals)

**Backend** (Python 3.10+):

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1          # macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
copy .env.example .env                # set OPENAI_API_KEY
uvicorn app.main:app --reload --port 8000
```

**Frontend** (Node 18+):

```powershell
cd frontend
npm install
npm run dev
```

Open http://localhost:5173.

---

## Try it with the sample documents

The [`samples/`](samples) folder contains ready-to-use documents:

- `service_agreement.txt` — a master services agreement
- `vendor_agreement.txt` — a similar software subscription agreement
- `invoice.txt` — a matching invoice

Suggested demo flow:

1. **Upload** all three on the Documents tab.
2. **Chat:** *"What are the payment terms and late fees?"* → see cited sources.
3. **Extract** on `service_agreement.txt` → people, dates, amounts, obligations…
4. **Compare** `service_agreement.txt` vs `vendor_agreement.txt`, focus on
   *"pricing and termination"*.
5. **Generate report** on any document and download the Markdown.

> AI features require `OPENAI_API_KEY` to be set in the backend environment.

---

## API endpoints

| Method | Path                | Description                       |
|--------|---------------------|-----------------------------------|
| GET    | `/health`           | Health + config status            |
| POST   | `/documents/upload` | Upload & index a document         |
| GET    | `/documents`        | List documents                    |
| GET    | `/documents/{id}`   | Document metadata                 |
| POST   | `/chat`             | RAG Q&A with citations            |
| POST   | `/extract`          | Structured field extraction       |
| POST   | `/summarize`        | Summarize a document              |
| POST   | `/compare`          | Compare two documents             |
| POST   | `/generate-report`  | Markdown intelligence report      |
| POST   | `/auth/keys`        | Mint an API key (admin token)     |
| GET    | `/auth/keys`        | List API keys (admin token)       |
| DELETE | `/auth/keys/{id}`   | Revoke an API key (admin token)   |
| GET    | `/usage`            | Calling key's usage counters      |
| GET    | `/auth/usage`       | Usage for all keys (admin token)  |

> **Auth:** with `AUTH_ENABLED=true` (default), data/AI endpoints require an
> `X-API-Key` header. Use a static key (`API_KEYS`) or mint one via `/auth`
> (`ADMIN_API_TOKEN`). In the UI, paste the key into the sidebar field. See
> [`backend/README.md`](backend/README.md#authentication-api-keys) for details.

---

## Testing & CI

```powershell
# Backend (offline — AI calls are monkeypatched)
cd backend; .\.venv\Scripts\python.exe -m pytest

# Frontend (type-check + build)
cd frontend; npm run build
```

GitHub Actions ([`.github/workflows/ci.yml`](.github/workflows/ci.yml)) runs the
backend lint + tests and the frontend type-check + build on every push and PR.

---

## Project layout

```
llamaindex-document-agent/
  backend/        FastAPI + LlamaIndex service (see backend/README.md)
  frontend/       React + Vite SPA (see frontend/README.md)
  samples/        Demo documents
  docker-compose.yml
  .github/workflows/ci.yml
  .env.example    Root env for docker compose
```

---

## Security & configuration notes

- **No secrets in code.** All keys come from environment variables / `.env`.
- `.env` files are git-ignored; only `.env.example` files are committed.
- **API key auth** guards data/AI endpoints (`X-API-Key`); managed keys are
  stored hashed (SHA-256) and minted via an admin-token-protected `/auth` API.
- **Per-key ownership:** each key sees and operates on only its own documents;
  RAG retrieval is filtered to the caller's chunks (cross-key access → `404`).
- **Per-key usage tracking:** request and operation counts are recorded per key
  (`GET /usage` for self, `GET /auth/usage` for an admin overview).
- For production scale: swap the local vector store for a managed vector DB
  (Chroma/Qdrant/pgvector) and add per-user accounts / rate limiting.
```
