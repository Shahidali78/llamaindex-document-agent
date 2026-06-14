# Screenshots

Add PNG screenshots here with these exact filenames so they render in the root
[`README.md`](../../README.md#screenshots):

| Filename          | What to capture |
|-------------------|-----------------|
| `documents.png`   | The **Documents** tab after uploading the sample docs (table with status badges). |
| `chat.png`        | The **Chat (RAG)** tab showing an answer with the source cards underneath. |
| `extract.png`     | The **Extract** tab showing the structured-field grid for a document. |
| `usage.png`       | The **Usage** tab showing the per-key stat cards. |

## How to capture

1. Run the stack (`backend` on :8000, `frontend` on :5173) with a real
   `OPENAI_API_KEY` set in `backend/.env`.
2. Open http://localhost:5173, paste your API key, and upload the files in
   [`../../samples`](../../samples).
3. Use the OS screenshot tool (Windows: `Win + Shift + S`) to grab each view and
   save it here with the filename above.

Tip: a ~1280px-wide capture looks crisp without bloating the repo.
