/**
 * TypeScript types for API responses
 */

export interface UploadResponse {
  document_id: number;
  filename: string;
  original_filename: string;
  file_size: number;
  mime_type: string;
  content_hash: string;
  job_id: number;
  status: string;
}

export interface BatchUploadResponse {
  batch_id: string;
  total: number;
  successful: number;
  failed: number;
  results: BatchUploadResult[];
}

export interface BatchUploadResult {
  filename: string;
  status: 'success' | 'error';
  document_id?: number;
  job_id?: number;
  error?: string;
  file_size?: number;
  mime_type?: string;
}

export interface JobStatus {
  job_id: number;
  document_id: number;
  status: 'uploaded' | 'processing' | 'completed' | 'failed';
  progress_percent: number;
  job_type: string;
  created_at: string;
  error_message?: string;
}

export interface Document {
  document_id: number;
  filename: string;
  original_filename: string;
  file_type: string;
  mime_type: string;
  file_size: number;
  processing_status: string;
  content_hash: string;
  uploaded_at: string;
  language?: string;
  page_count?: number;
}

export interface ResumableUploadSession {
  session_id: string;
  filename: string;
  file_size: number;
  chunk_size: number;
  total_chunks: number;
  uploaded_bytes: number;
  status: string;
  upload_url: string;
  expires_at: string;
  created_at: string;
}

export interface ChunkUploadProgress {
  session_id: string;
  uploaded_bytes: number;
  total_bytes: number;
  progress_percent: number;
  status: string;
  document_id?: number;
  job_id?: number;
}

export class ApiError extends Error {
  constructor(
    public statusCode: number,
    public errorType: string,
    message: string
  ) {
    super(message);
    this.name = 'ApiError';
  }
}
