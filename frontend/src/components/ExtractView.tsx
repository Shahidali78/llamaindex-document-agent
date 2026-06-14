import { useState } from "react";
import { api, ApiError } from "../api/client";
import type { DocumentResponse, ExtractionResult } from "../types";
import { Button, Card, EmptyState, ErrorBanner } from "./ui/primitives";
import { DocumentSelect } from "./DocumentSelect";

interface Props {
  documents: DocumentResponse[];
}

function FieldList({ label, items }: { label: string; items: string[] }) {
  return (
    <div className="rounded-lg border border-slate-800 bg-slate-800/40 p-3">
      <h4 className="mb-2 text-xs font-semibold uppercase tracking-wide text-indigo-300">
        {label}
      </h4>
      {items.length === 0 ? (
        <p className="text-xs italic text-slate-500">None identified.</p>
      ) : (
        <ul className="list-disc space-y-1 pl-4 text-sm text-slate-200">
          {items.map((item, i) => (
            <li key={i}>{item}</li>
          ))}
        </ul>
      )}
    </div>
  );
}

export function ExtractView({ documents }: Props) {
  const [docId, setDocId] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<ExtractionResult | null>(null);

  async function run() {
    if (!docId) return;
    setLoading(true);
    setError(null);
    setResult(null);
    try {
      const res = await api.extract(docId);
      setResult(res.extraction);
    } catch (e) {
      setError(e instanceof ApiError ? e.message : "Extraction failed.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="space-y-6">
      <Card
        title="Structured extraction"
        subtitle="Pull key fields — people, dates, amounts, obligations, risks, action items — from a document."
      >
        <div className="flex flex-wrap items-end gap-3">
          <div className="min-w-64 flex-1">
            <DocumentSelect documents={documents} value={docId} onChange={setDocId} />
          </div>
          <Button onClick={run} loading={loading} disabled={!docId}>
            Extract
          </Button>
        </div>
        <div className="mt-3">
          <ErrorBanner message={error} />
        </div>
      </Card>

      {result && (
        <Card title={result.title || "Extracted fields"}>
          <div className="mb-4 flex flex-wrap gap-3 text-sm">
            <span className="rounded-full bg-slate-800 px-3 py-1 text-slate-300">
              Type: <span className="text-indigo-300">{result.document_type || "unknown"}</span>
            </span>
          </div>

          <div className="grid gap-3 md:grid-cols-2">
            <FieldList label="Key people" items={result.key_people} />
            <FieldList label="Key dates" items={result.key_dates} />
            <FieldList label="Prices / amounts" items={result.prices_or_amounts} />
            <FieldList label="Obligations" items={result.obligations} />
            <FieldList label="Risks" items={result.risks} />
            <FieldList label="Action items" items={result.action_items} />
          </div>

          <div className="mt-4 rounded-lg border border-slate-800 bg-slate-800/40 p-3">
            <h4 className="mb-2 text-xs font-semibold uppercase tracking-wide text-indigo-300">
              Summary
            </h4>
            <p className="text-sm leading-relaxed text-slate-200">
              {result.summary || "—"}
            </p>
          </div>
        </Card>
      )}

      {!result && !loading && (
        <EmptyState>Select an indexed document and click Extract.</EmptyState>
      )}
    </div>
  );
}
