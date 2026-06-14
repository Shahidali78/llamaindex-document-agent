// Typed API client for the FastAPI backend.

import type {
  ChatRequest,
  ChatResponse,
  CompareResponse,
  DocumentListResponse,
  DocumentResponse,
  ExtractResponse,
  HealthResponse,
  ReportResponse,
  SummarizeResponse,
  UploadResponse,
  UsageResponse,
} from "../types";

const BASE_URL = (
  import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000"
).replace(/\/$/, "");

const API_KEY_STORAGE = "docintel_api_key";

/** Read the saved API key (from localStorage). */
export function getApiKey(): string {
  return localStorage.getItem(API_KEY_STORAGE) ?? "";
}

/** Save or clear the API key. */
export function setApiKey(value: string): void {
  if (value) localStorage.setItem(API_KEY_STORAGE, value);
  else localStorage.removeItem(API_KEY_STORAGE);
}

/** Merge the API key header into a set of headers (if a key is set). */
function withAuth(headers: Record<string, string> = {}): Record<string, string> {
  const key = getApiKey();
  return key ? { ...headers, "X-API-Key": key } : headers;
}

export class ApiError extends Error {
  status: number;
  constructor(message: string, status: number) {
    super(message);
    this.name = "ApiError";
    this.status = status;
  }
}

async function parseError(res: Response): Promise<never> {
  let detail = `Request failed (${res.status})`;
  try {
    const body = await res.json();
    if (body?.detail) {
      detail =
        typeof body.detail === "string"
          ? body.detail
          : JSON.stringify(body.detail);
    } else if (body?.error) {
      detail = body.error;
    }
  } catch {
    /* non-JSON body */
  }
  throw new ApiError(detail, res.status);
}

async function getJson<T>(path: string): Promise<T> {
  const res = await fetch(`${BASE_URL}${path}`, { headers: withAuth() });
  if (!res.ok) return parseError(res);
  return res.json() as Promise<T>;
}

async function postJson<T>(path: string, body: unknown): Promise<T> {
  const res = await fetch(`${BASE_URL}${path}`, {
    method: "POST",
    headers: withAuth({ "Content-Type": "application/json" }),
    body: JSON.stringify(body),
  });
  if (!res.ok) return parseError(res);
  return res.json() as Promise<T>;
}

export const api = {
  baseUrl: BASE_URL,

  health: () => getJson<HealthResponse>("/health"),

  listDocuments: () => getJson<DocumentListResponse>("/documents"),

  getDocument: (id: string) => getJson<DocumentResponse>(`/documents/${id}`),

  uploadDocument: async (file: File): Promise<UploadResponse> => {
    const form = new FormData();
    form.append("file", file);
    const res = await fetch(`${BASE_URL}/documents/upload`, {
      method: "POST",
      headers: withAuth(),
      body: form,
    });
    if (!res.ok) return parseError(res);
    return res.json() as Promise<UploadResponse>;
  },

  chat: (req: ChatRequest) => postJson<ChatResponse>("/chat", req),

  extract: (documentId: string) =>
    postJson<ExtractResponse>("/extract", { document_id: documentId }),

  summarize: (documentId: string, style = "concise") =>
    postJson<SummarizeResponse>("/summarize", {
      document_id: documentId,
      style,
    }),

  compare: (idA: string, idB: string, focus = "") =>
    postJson<CompareResponse>("/compare", {
      document_id_a: idA,
      document_id_b: idB,
      focus,
    }),

  generateReport: (documentId: string) =>
    postJson<ReportResponse>("/generate-report", { document_id: documentId }),

  usage: () => getJson<UsageResponse>("/usage"),
};
