# Deploying to Render

This repo ships a [Render Blueprint](../render.yaml) that provisions **both**
services from one file:

- **docintel-backend** — the FastAPI + LlamaIndex API, built from
  `backend/Dockerfile` (Docker Web Service).
- **docintel-frontend** — the React/Vite app, built and served as a Static Site.

## One-time setup

1. **Push the repo to GitHub** (already done) so Render can read `render.yaml`.

2. In the [Render dashboard](https://dashboard.render.com): **New + → Blueprint**,
   select this repository, and confirm. Render reads `render.yaml` and shows both
   services. *(Or use the "Deploy to Render" button in the root README.)*

3. **Enter the prompted secrets** (the `sync: false` vars):

   | Service  | Variable           | Value                                            |
   |----------|--------------------|--------------------------------------------------|
   | backend  | `OPENAI_API_KEY`   | your real OpenAI key                             |
   | backend  | `API_KEYS`         | a demo key, e.g. `demo-key-123`                  |
   | backend  | `ADMIN_API_TOKEN`  | any strong string (enables `/auth` key minting)  |
   | frontend | `VITE_API_BASE_URL`| `https://docintel-backend.onrender.com` *(see 5)*|

4. Click **Apply**. Render builds the Docker backend and the static frontend.

5. **Fix the frontend → backend URL.** When the backend finishes, copy its real
   URL from the dashboard (usually `https://docintel-backend.onrender.com`, but
   Render may append a suffix if the name is taken). If it differs from what you
   entered in step 3, update the frontend's `VITE_API_BASE_URL` and click
   **Manual Deploy → Deploy latest commit** on the frontend service (the URL is
   baked in at build time).

## Using the live app

1. Open the **frontend** URL (`https://docintel-frontend.onrender.com`).
2. Paste the `API_KEYS` value you set into the sidebar **API key** field.
3. Upload a doc from [`../samples`](../samples) and try Chat / Extract / etc.

Backend docs are at `https://docintel-backend.onrender.com/docs`.

## Things to know (free tier)

- **Cold starts:** free services sleep after ~15 min idle and take ~30–60s to
  wake on the next request. The first request after a sleep may be slow.
- **Ephemeral storage:** uploads, the vector index, and the SQLite DB live on the
  container's disk, which is wiped on every redeploy/cold start. Re-upload after
  a restart. For persistence, set the backend `plan` to `starter` and uncomment
  the `disk:` block in `render.yaml` (a small monthly cost).
- **CORS** defaults to `*` for the demo. To lock it down, set the backend
  `CORS_ORIGINS` to your frontend URL.

## Updating

Both services have `autoDeploy: true`, so a `git push` to `main` triggers a
rebuild and redeploy automatically.
