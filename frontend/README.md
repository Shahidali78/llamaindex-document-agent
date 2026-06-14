# LlamaIndex AI Document Intelligence Platform — Frontend

A single-page **React + TypeScript + Vite + Tailwind CSS v4** UI for the
FastAPI document-intelligence backend. It provides a clean SaaS-style dashboard
for all backend capabilities:

- 📄 **Documents** — drag-free upload (PDF/TXT/DOCX) with live status & metadata
- 💬 **Chat (RAG)** — ask questions, see answers with source citations & scores
- 🧾 **Extract** — structured fields in a tidy grid
- 📝 **Summarize** — multiple summary styles
- 🔍 **Compare** — side-by-side comparison of two documents
- 📊 **Report** — generate & download a Markdown intelligence report

A sidebar status indicator shows whether the backend is online and whether the
OpenAI key is configured.

---

## Prerequisites

- **Node.js 18+** (tested on Node 24)
- The backend running (see `../backend/README.md`)

---

## Setup & run

```powershell
cd C:\MY_Projects\llamaindex-document-agent\frontend

# 1. Install dependencies
npm install

# 2. (Optional) point at a non-default backend URL
copy .env.example .env   # edit VITE_API_BASE_URL if needed (default http://localhost:8000)

# 3. Start the dev server
npm run dev
```

Then open **http://localhost:5173**.

> The backend already enables permissive CORS (`CORS_ORIGINS=*` by default), so
> the dev server can call it directly.

### Other scripts

```powershell
npm run build     # type-check + production build to dist/
npm run preview   # serve the production build locally
npm run lint      # TypeScript type-check (no emit)
```

---

## How it talks to the backend

`src/api/client.ts` is a typed wrapper around `fetch`. The base URL comes from
`VITE_API_BASE_URL` (default `http://localhost:8000`). Errors from the API are
surfaced via the `ApiError` class and shown inline in each view.

Types in `src/types.ts` mirror the backend Pydantic schemas.

---

## Project structure

```
frontend/
  index.html
  vite.config.ts            # React + Tailwind v4 plugins
  src/
    main.tsx
    App.tsx                 # Sidebar nav + shared document state + health status
    index.css               # Tailwind import + markdown styles
    types.ts                # API types (mirror backend schemas)
    api/client.ts           # Typed fetch client + ApiError
    components/
      DocumentsView.tsx      # Upload + documents table
      ChatView.tsx           # RAG chat with scope filter + sources
      ExtractView.tsx        # Structured field grid
      SummarizeView.tsx      # Summary with style picker
      CompareView.tsx        # Two-document comparison
      ReportView.tsx         # Report render + .md download
      DocumentSelect.tsx     # Reusable indexed-document dropdown
      ui/primitives.tsx      # Button, Card, Badge, Spinner, Markdown, etc.
```

---

## Quick start (full stack)

In two terminals:

```powershell
# Terminal 1 — backend
cd C:\MY_Projects\llamaindex-document-agent\backend
.\.venv\Scripts\Activate.ps1
uvicorn app.main:app --reload --port 8000

# Terminal 2 — frontend
cd C:\MY_Projects\llamaindex-document-agent\frontend
npm run dev
```

Open http://localhost:5173, upload a document, then explore Chat / Extract /
Summarize / Compare / Report. (AI features need `OPENAI_API_KEY` set in the
backend `.env`.)
```
