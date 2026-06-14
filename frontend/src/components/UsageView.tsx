import { useCallback, useEffect, useState } from "react";
import { api, ApiError } from "../api/client";
import type { UsageResponse } from "../types";
import { Button, Card, ErrorBanner } from "./ui/primitives";

function Stat({ label, value }: { label: string; value: number }) {
  return (
    <div className="rounded-lg border border-slate-800 bg-slate-800/40 p-4 text-center">
      <div className="text-2xl font-bold text-indigo-300">{value}</div>
      <div className="mt-1 text-xs uppercase tracking-wide text-slate-400">
        {label}
      </div>
    </div>
  );
}

export function UsageView() {
  const [usage, setUsage] = useState<UsageResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      setUsage(await api.usage());
    } catch (e) {
      setError(
        e instanceof ApiError && e.status === 401
          ? "Enter a valid API key in the sidebar to view usage."
          : e instanceof ApiError
            ? e.message
            : "Failed to load usage.",
      );
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    load();
  }, [load]);

  return (
    <div className="space-y-6">
      <Card
        title="Your usage"
        subtitle="Per-key request and operation counts for the current API key."
      >
        <div className="mb-4">
          <Button variant="secondary" onClick={load} loading={loading}>
            Refresh
          </Button>
        </div>

        <ErrorBanner message={error} />

        {usage && (
          <>
            <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
              <Stat label="Total requests" value={usage.total_requests} />
              <Stat label="Documents" value={usage.document_count} />
              <Stat label="Uploads" value={usage.uploads} />
              <Stat label="Chats" value={usage.chats} />
              <Stat label="Extractions" value={usage.extractions} />
              <Stat label="Summaries" value={usage.summaries} />
              <Stat label="Comparisons" value={usage.comparisons} />
              <Stat label="Reports" value={usage.reports} />
            </div>

            <dl className="mt-5 space-y-1 text-xs text-slate-400">
              <div className="flex gap-2">
                <dt className="font-medium text-slate-300">Owner id:</dt>
                <dd>
                  <code>{usage.owner_id}</code>
                  {usage.name ? ` (${usage.name})` : ""}
                </dd>
              </div>
              {usage.last_request_at && (
                <div className="flex gap-2">
                  <dt className="font-medium text-slate-300">Last request:</dt>
                  <dd>{new Date(usage.last_request_at).toLocaleString()}</dd>
                </div>
              )}
            </dl>
          </>
        )}
      </Card>
    </div>
  );
}
