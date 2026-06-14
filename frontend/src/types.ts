// Type definitions mirroring the FastAPI backend schemas.

export interface HealthResponse {
  status: string;
  app: string;
  environment: string;
  openai_configured: boolean;
  auth_enabled: boolean;
}

export interface DocumentResponse {
  id: string;
  filename: string;
  file_type: string;
  size_bytes: number;
  num_chunks: number;
  status: string; // pending | indexed | failed
  error: string | null;
  created_at: string;
}

export interface DocumentListResponse {
  count: number;
  documents: DocumentResponse[];
}

export interface UploadResponse {
  message: string;
  document: DocumentResponse;
}

export interface SourceNode {
  document_id: string | null;
  filename: string | null;
  snippet: string;
  score: number | null;
}

export interface ChatRequest {
  question: string;
  document_ids?: string[] | null;
  top_k?: number | null;
}

export interface ChatResponse {
  answer: string;
  sources: SourceNode[];
}

export interface ExtractionResult {
  document_type: string;
  title: string;
  key_people: string[];
  key_dates: string[];
  prices_or_amounts: string[];
  obligations: string[];
  risks: string[];
  action_items: string[];
  summary: string;
}

export interface ExtractResponse {
  document_id: string;
  filename: string;
  extraction: ExtractionResult;
}

export interface SummarizeResponse {
  document_id: string;
  filename: string;
  summary: string;
}

export interface CompareResponse {
  document_id_a: string;
  document_id_b: string;
  filename_a: string;
  filename_b: string;
  comparison: string;
}

export interface ReportResponse {
  document_id: string;
  filename: string;
  report_markdown: string;
  extraction: ExtractionResult | null;
  summary: string | null;
}

export interface UsageResponse {
  owner_id: string;
  name: string | null;
  total_requests: number;
  uploads: number;
  chats: number;
  extractions: number;
  summaries: number;
  comparisons: number;
  reports: number;
  document_count: number;
  created_at: string | null;
  last_request_at: string | null;
}
