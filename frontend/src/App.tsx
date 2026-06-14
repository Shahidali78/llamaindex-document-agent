import { useCallback, useEffect, useState } from "react";
import { api, ApiError } from "./api/client";
import type { DocumentResponse, HealthResponse } from "./types";
import { ApiKeySettings } from "./components/ApiKeySettings";
import { ChatView } from "./components/ChatView";
import { CompareView } from "./components/CompareView";
import { DocumentsView } from "./components/DocumentsView";
import { ExtractView } from "./components/ExtractView";
import { ReportView } from "./components/ReportView";
import { SummarizeView } from "./components/SummarizeView";
import { UsageView } from "./components/UsageView";

type ViewKey =
  | "documents"
  | "chat"
  | "extract"
  | "summarize"
  | "compare"
  | "report"
  | "usage";

const NAV: { key: ViewKey; label: string; icon: string }[] = [
  { key: "documents", label: "Documents", icon: "📄" },
  { key: "chat", label: "Chat (RAG)", icon: "💬" },
  { key: "extract", label: "Extract", icon: "🧾" },
  { key: "summarize", label: "Summarize", icon: "📝" },
  { key: "compare", label: "Compare", icon: "🔍" },
  { key: "report", label: "Report", icon: "📊" },
  { key: "usage", label: "Usage", icon: "📈" },
];

export default function App() {
  const [view, setView] = useState<ViewKey>("documents");
  const [documents, setDocuments] = useState<DocumentResponse[]>([]);
  const [loadingDocs, setLoadingDocs] = useState(false);
  const [health, setHealth] = useState<HealthResponse | null>(null);
  const [globalError, setGlobalError] = useState<string | null>(null);

  const refreshDocuments = useCallback(async () => {
    setLoadingDocs(true);
    setGlobalError(null);
    try {
      const res = await api.listDocuments();
      setDocuments(res.documents);
    } catch (e) {
      if (e instanceof ApiError && e.status === 401) {
        setGlobalError(
          "Authentication required. Enter a valid API key in the sidebar.",
        );
      } else {
        setGlobalError(
          e instanceof ApiError
            ? `Cannot reach backend at ${api.baseUrl}: ${e.message}`
            : `Cannot reach backend at ${api.baseUrl}.`,
        );
      }
    } finally {
      setLoadingDocs(false);
    }
  }, []);

  const reloadAll = useCallback(() => {
    api.health().then(setHealth).catch(() => setHealth(null));
    refreshDocuments();
  }, [refreshDocuments]);

  useEffect(() => {
    reloadAll();
  }, [reloadAll]);

  return (
    <div className="flex min-h-screen">
      {/* Sidebar */}
      <aside className="flex w-60 flex-col border-r border-slate-800 bg-slate-900/80 p-4">
        <div className="mb-6 flex items-center gap-2">
          <img src="/favicon.svg" alt="logo" className="h-8 w-8" />
          <div>
            <h1 className="text-sm font-bold leading-tight text-slate-100">
              DocIntel
            </h1>
            <p className="text-xs text-slate-500">LlamaIndex platform</p>
          </div>
        </div>

        <nav className="flex flex-1 flex-col gap-1">
          {NAV.map((item) => (
            <button
              key={item.key}
              onClick={() => setView(item.key)}
              className={`flex items-center gap-3 rounded-lg px-3 py-2 text-left text-sm transition ${
                view === item.key
                  ? "bg-indigo-600/20 font-medium text-indigo-200"
                  : "text-slate-400 hover:bg-slate-800 hover:text-slate-200"
              }`}
            >
              <span aria-hidden>{item.icon}</span>
              {item.label}
            </button>
          ))}
        </nav>

        {/* API key (only relevant when auth is enabled) */}
        {(health?.auth_enabled ?? true) && (
          <div className="mt-4">
            <ApiKeySettings onChange={reloadAll} />
          </div>
        )}

        {/* Backend status */}
        <div className="mt-3 rounded-lg border border-slate-800 bg-slate-800/40 p-3 text-xs">
          <div className="flex items-center gap-2">
            <span
              className={`h-2 w-2 rounded-full ${
                health ? "bg-emerald-400" : "bg-rose-400"
              }`}
            />
            <span className="text-slate-300">
              {health ? "Backend online" : "Backend offline"}
            </span>
          </div>
          {health && !health.openai_configured && (
            <p className="mt-2 text-amber-300">
              ⚠ OpenAI key not set — AI features will return errors.
            </p>
          )}
        </div>
      </aside>

      {/* Main */}
      <main className="flex-1 overflow-y-auto">
        <div className="mx-auto max-w-4xl px-6 py-8">
          <header className="mb-6">
            <h2 className="text-2xl font-bold text-slate-100">
              {NAV.find((n) => n.key === view)?.label}
            </h2>
          </header>

          {globalError && (
            <div className="mb-6 rounded-lg border border-rose-500/30 bg-rose-500/10 px-4 py-3 text-sm text-rose-200">
              {globalError}
            </div>
          )}

          {view === "documents" && (
            <DocumentsView
              documents={documents}
              loading={loadingDocs}
              onRefresh={refreshDocuments}
            />
          )}
          {view === "chat" && <ChatView documents={documents} />}
          {view === "extract" && <ExtractView documents={documents} />}
          {view === "summarize" && <SummarizeView documents={documents} />}
          {view === "compare" && <CompareView documents={documents} />}
          {view === "report" && <ReportView documents={documents} />}
          {view === "usage" && <UsageView />}
        </div>
      </main>
    </div>
  );
}
