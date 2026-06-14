import { useState } from "react";
import { api, ApiError } from "../api/client";
import type { DocumentResponse } from "../types";
import { Button, Card, EmptyState, ErrorBanner, Markdown } from "./ui/primitives";
import { DocumentSelect } from "./DocumentSelect";

interface Props {
  documents: DocumentResponse[];
}

export function CompareView({ documents }: Props) {
  const [idA, setIdA] = useState("");
  const [idB, setIdB] = useState("");
  const [focus, setFocus] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [comparison, setComparison] = useState<string | null>(null);

  const sameDoc = idA !== "" && idA === idB;

  async function run() {
    if (!idA || !idB || sameDoc) return;
    setLoading(true);
    setError(null);
    setComparison(null);
    try {
      const res = await api.compare(idA, idB, focus.trim());
      setComparison(res.comparison);
    } catch (e) {
      setError(e instanceof ApiError ? e.message : "Comparison failed.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="space-y-6">
      <Card
        title="Compare two documents"
        subtitle="Highlight similarities, differences, and unique items across two documents."
      >
        <div className="grid gap-3 md:grid-cols-2">
          <DocumentSelect
            documents={documents}
            value={idA}
            onChange={setIdA}
            label="Document A"
          />
          <DocumentSelect
            documents={documents}
            value={idB}
            onChange={setIdB}
            label="Document B"
          />
        </div>

        <label className="mt-3 block">
          <span className="mb-1 block text-sm font-medium text-slate-300">
            Focus (optional)
          </span>
          <input
            value={focus}
            onChange={(e) => setFocus(e.target.value)}
            placeholder="e.g. pricing, obligations, termination clauses"
            className="w-full rounded-lg border border-slate-700 bg-slate-800 px-3 py-2 text-sm text-slate-100 placeholder:text-slate-500 focus:border-indigo-500 focus:outline-none"
          />
        </label>

        {sameDoc && (
          <p className="mt-2 text-sm text-amber-300">
            Please choose two different documents.
          </p>
        )}

        <div className="mt-4">
          <Button
            onClick={run}
            loading={loading}
            disabled={!idA || !idB || sameDoc}
          >
            Compare
          </Button>
        </div>
        <div className="mt-3">
          <ErrorBanner message={error} />
        </div>
      </Card>

      {comparison ? (
        <Card title="Comparison">
          <Markdown>{comparison}</Markdown>
        </Card>
      ) : (
        !loading && <EmptyState>Pick two documents and click Compare.</EmptyState>
      )}
    </div>
  );
}
