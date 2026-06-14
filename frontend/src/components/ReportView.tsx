import { useState } from "react";
import { api, ApiError } from "../api/client";
import type { DocumentResponse, ReportResponse } from "../types";
import { Button, Card, EmptyState, ErrorBanner, Markdown } from "./ui/primitives";
import { DocumentSelect } from "./DocumentSelect";

interface Props {
  documents: DocumentResponse[];
}

export function ReportView({ documents }: Props) {
  const [docId, setDocId] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [report, setReport] = useState<ReportResponse | null>(null);

  async function run() {
    if (!docId) return;
    setLoading(true);
    setError(null);
    setReport(null);
    try {
      const res = await api.generateReport(docId);
      setReport(res);
    } catch (e) {
      setError(e instanceof ApiError ? e.message : "Report generation failed.");
    } finally {
      setLoading(false);
    }
  }

  function download() {
    if (!report) return;
    const blob = new Blob([report.report_markdown], { type: "text/markdown" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `${report.filename.replace(/\.[^.]+$/, "")}-report.md`;
    a.click();
    URL.revokeObjectURL(url);
  }

  return (
    <div className="space-y-6">
      <Card
        title="Generate report"
        subtitle="Produce a combined intelligence report (structured fields + summary) as Markdown."
      >
        <div className="flex flex-wrap items-end gap-3">
          <div className="min-w-64 flex-1">
            <DocumentSelect documents={documents} value={docId} onChange={setDocId} />
          </div>
          <Button onClick={run} loading={loading} disabled={!docId}>
            Generate
          </Button>
        </div>
        <div className="mt-3">
          <ErrorBanner message={error} />
        </div>
      </Card>

      {report ? (
        <Card title="Report">
          <div className="mb-3">
            <Button variant="secondary" onClick={download}>
              Download .md
            </Button>
          </div>
          <div className="rounded-lg border border-slate-800 bg-slate-800/30 p-4">
            <Markdown>{report.report_markdown}</Markdown>
          </div>
        </Card>
      ) : (
        !loading && <EmptyState>Select a document and click Generate.</EmptyState>
      )}
    </div>
  );
}
