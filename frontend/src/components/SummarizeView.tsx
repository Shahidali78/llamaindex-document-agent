import { useState } from "react";
import { api, ApiError } from "../api/client";
import type { DocumentResponse } from "../types";
import { Button, Card, EmptyState, ErrorBanner, Markdown } from "./ui/primitives";
import { DocumentSelect } from "./DocumentSelect";

interface Props {
  documents: DocumentResponse[];
}

const STYLES = ["concise", "detailed", "bullet points", "executive summary"];

export function SummarizeView({ documents }: Props) {
  const [docId, setDocId] = useState("");
  const [style, setStyle] = useState("concise");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [summary, setSummary] = useState<string | null>(null);

  async function run() {
    if (!docId) return;
    setLoading(true);
    setError(null);
    setSummary(null);
    try {
      const res = await api.summarize(docId, style);
      setSummary(res.summary);
    } catch (e) {
      setError(e instanceof ApiError ? e.message : "Summarization failed.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="space-y-6">
      <Card
        title="Summarize"
        subtitle="Generate a summary of a document in your preferred style."
      >
        <div className="flex flex-wrap items-end gap-3">
          <div className="min-w-64 flex-1">
            <DocumentSelect documents={documents} value={docId} onChange={setDocId} />
          </div>
          <label className="block">
            <span className="mb-1 block text-sm font-medium text-slate-300">
              Style
            </span>
            <select
              value={style}
              onChange={(e) => setStyle(e.target.value)}
              className="rounded-lg border border-slate-700 bg-slate-800 px-3 py-2 text-sm text-slate-100 focus:border-indigo-500 focus:outline-none"
            >
              {STYLES.map((s) => (
                <option key={s} value={s}>
                  {s}
                </option>
              ))}
            </select>
          </label>
          <Button onClick={run} loading={loading} disabled={!docId}>
            Summarize
          </Button>
        </div>
        <div className="mt-3">
          <ErrorBanner message={error} />
        </div>
      </Card>

      {summary ? (
        <Card title="Summary">
          <Markdown>{summary}</Markdown>
        </Card>
      ) : (
        !loading && <EmptyState>Select a document and click Summarize.</EmptyState>
      )}
    </div>
  );
}
