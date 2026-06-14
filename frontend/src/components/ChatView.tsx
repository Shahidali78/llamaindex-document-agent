import { useState } from "react";
import { api, ApiError } from "../api/client";
import type { ChatResponse, DocumentResponse } from "../types";
import { Button, Card, EmptyState, ErrorBanner } from "./ui/primitives";

interface Props {
  documents: DocumentResponse[];
}

export function ChatView({ documents }: Props) {
  const [question, setQuestion] = useState("");
  const [selected, setSelected] = useState<string[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<ChatResponse | null>(null);

  const indexed = documents.filter((d) => d.status === "indexed");

  function toggle(id: string) {
    setSelected((prev) =>
      prev.includes(id) ? prev.filter((x) => x !== id) : [...prev, id],
    );
  }

  async function ask() {
    if (!question.trim()) return;
    setLoading(true);
    setError(null);
    setResult(null);
    try {
      const res = await api.chat({
        question: question.trim(),
        document_ids: selected.length ? selected : null,
      });
      setResult(res);
    } catch (e) {
      setError(e instanceof ApiError ? e.message : "Chat request failed.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="space-y-6">
      <Card
        title="Ask your documents"
        subtitle="Retrieval-augmented answers with source citations. Optionally scope the search to specific documents."
      >
        <textarea
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === "Enter" && (e.metaKey || e.ctrlKey)) ask();
          }}
          rows={3}
          placeholder="e.g. What are the payment terms and key deadlines?"
          className="w-full resize-y rounded-lg border border-slate-700 bg-slate-800 px-3 py-2 text-sm text-slate-100 placeholder:text-slate-500 focus:border-indigo-500 focus:outline-none"
        />

        {indexed.length > 0 && (
          <div className="mt-3">
            <p className="mb-1 text-xs font-medium uppercase tracking-wide text-slate-500">
              Scope (optional — defaults to all)
            </p>
            <div className="flex flex-wrap gap-2">
              {indexed.map((d) => (
                <label
                  key={d.id}
                  className={`cursor-pointer rounded-full border px-3 py-1 text-xs transition ${
                    selected.includes(d.id)
                      ? "border-indigo-500 bg-indigo-500/20 text-indigo-200"
                      : "border-slate-700 bg-slate-800 text-slate-300 hover:border-slate-500"
                  }`}
                >
                  <input
                    type="checkbox"
                    className="hidden"
                    checked={selected.includes(d.id)}
                    onChange={() => toggle(d.id)}
                  />
                  {d.filename}
                </label>
              ))}
            </div>
          </div>
        )}

        <div className="mt-4 flex items-center gap-3">
          <Button onClick={ask} loading={loading} disabled={!question.trim()}>
            Ask
          </Button>
          <span className="text-xs text-slate-500">⌘/Ctrl + Enter</span>
        </div>
        <div className="mt-3">
          <ErrorBanner message={error} />
        </div>
      </Card>

      {result && (
        <Card title="Answer">
          <p className="whitespace-pre-wrap text-sm leading-relaxed text-slate-100">
            {result.answer}
          </p>

          <h3 className="mt-5 mb-2 text-sm font-semibold text-slate-300">
            Sources ({result.sources.length})
          </h3>
          {result.sources.length === 0 ? (
            <EmptyState>No source chunks were returned.</EmptyState>
          ) : (
            <div className="space-y-3">
              {result.sources.map((s, i) => (
                <div
                  key={i}
                  className="rounded-lg border border-slate-800 bg-slate-800/40 p-3"
                >
                  <div className="mb-1 flex items-center justify-between">
                    <span className="text-xs font-medium text-indigo-300">
                      {s.filename ?? "Unknown document"}
                    </span>
                    {s.score != null && (
                      <span className="text-xs text-slate-500">
                        score {s.score.toFixed(3)}
                      </span>
                    )}
                  </div>
                  <p className="text-xs leading-relaxed text-slate-400">
                    {s.snippet}
                  </p>
                </div>
              ))}
            </div>
          )}
        </Card>
      )}
    </div>
  );
}
