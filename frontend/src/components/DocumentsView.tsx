import { useRef, useState } from "react";
import { api, ApiError } from "../api/client";
import type { DocumentResponse } from "../types";
import {
  Badge,
  Button,
  Card,
  EmptyState,
  ErrorBanner,
  formatBytes,
} from "./ui/primitives";

interface Props {
  documents: DocumentResponse[];
  loading: boolean;
  onRefresh: () => void;
}

const ACCEPTED = ".pdf,.txt,.docx";

export function DocumentsView({ documents, loading, onRefresh }: Props) {
  const inputRef = useRef<HTMLInputElement>(null);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [notice, setNotice] = useState<string | null>(null);

  async function handleUpload(file: File) {
    setUploading(true);
    setError(null);
    setNotice(null);
    try {
      const res = await api.uploadDocument(file);
      setNotice(`Uploaded & indexed "${res.document.filename}".`);
      onRefresh();
    } catch (e) {
      setError(e instanceof ApiError ? e.message : "Upload failed.");
    } finally {
      setUploading(false);
      if (inputRef.current) inputRef.current.value = "";
    }
  }

  return (
    <div className="space-y-6">
      <Card
        title="Upload a document"
        subtitle="Supported: PDF, TXT, DOCX. Files are stored locally, then chunked and indexed."
      >
        <div className="flex flex-wrap items-center gap-3">
          <input
            ref={inputRef}
            type="file"
            accept={ACCEPTED}
            disabled={uploading}
            onChange={(e) => {
              const file = e.target.files?.[0];
              if (file) handleUpload(file);
            }}
            className="block w-full max-w-md text-sm text-slate-300 file:mr-4 file:rounded-lg file:border-0 file:bg-indigo-600 file:px-4 file:py-2 file:text-sm file:font-medium file:text-white hover:file:bg-indigo-500"
          />
          {uploading && (
            <span className="text-sm text-slate-400">Indexing…</span>
          )}
        </div>
        <div className="mt-3 space-y-2">
          <ErrorBanner message={error} />
          {notice && (
            <div className="rounded-lg border border-emerald-500/30 bg-emerald-500/10 px-4 py-2 text-sm text-emerald-200">
              {notice}
            </div>
          )}
        </div>
      </Card>

      <Card
        title={`Documents (${documents.length})`}
        subtitle="All uploaded documents and their indexing status."
      >
        <div className="mb-3">
          <Button variant="secondary" onClick={onRefresh} loading={loading}>
            Refresh
          </Button>
        </div>

        {documents.length === 0 ? (
          <EmptyState>No documents yet. Upload one above to get started.</EmptyState>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm">
              <thead className="text-xs uppercase tracking-wide text-slate-500">
                <tr>
                  <th className="px-3 py-2">Filename</th>
                  <th className="px-3 py-2">Type</th>
                  <th className="px-3 py-2">Size</th>
                  <th className="px-3 py-2">Chunks</th>
                  <th className="px-3 py-2">Status</th>
                  <th className="px-3 py-2">Uploaded</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800">
                {documents.map((d) => (
                  <tr key={d.id} className="hover:bg-slate-800/40">
                    <td className="px-3 py-2 font-medium text-slate-200">
                      {d.filename}
                    </td>
                    <td className="px-3 py-2 text-slate-400">{d.file_type}</td>
                    <td className="px-3 py-2 text-slate-400">
                      {formatBytes(d.size_bytes)}
                    </td>
                    <td className="px-3 py-2 text-slate-400">{d.num_chunks}</td>
                    <td className="px-3 py-2">
                      <Badge status={d.status} />
                    </td>
                    <td className="px-3 py-2 text-slate-400">
                      {new Date(d.created_at).toLocaleString()}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </Card>
    </div>
  );
}
