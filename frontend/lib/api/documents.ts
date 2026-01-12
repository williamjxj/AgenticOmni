/**
 * API client for document management endpoints
 * Feature: 005-view-embedded-docs
 */

import {
  ApiError,
  Document,
  DocumentDetailResponse,
  DocumentFilters,
  DocumentListResponse,
  ChunkListResponse,
  TextPreviewResponse,
  EmbeddingStatistics,
  SortOptions,
} from '@/lib/types/document';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
const API_PREFIX = '/api/v1';

/**
 * Handle API response and throw errors if needed
 */
async function handleResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    const error = await response.json().catch(() => ({
      error: { message: 'Unknown error occurred', type: 'unknown' },
    }));
    throw new ApiError(
      response.status,
      error.error?.type || 'unknown',
      error.error?.message || `HTTP ${response.status}`,
      error.error?.details
    );
  }
  return response.json();
}

/**
 * Build query string from filters
 */
function buildQueryParams(
  filters: DocumentFilters,
  sort?: SortOptions
): URLSearchParams {
  const params = new URLSearchParams();

  // Always include tenant_id (default to 1 for now)
  params.append('tenant_id', '1');

  // Pagination
  if (filters.page) params.append('page', filters.page.toString());
  if (filters.page_size) params.append('limit', filters.page_size.toString());

  // Filters
  if (filters.file_type) {
    filters.file_type.forEach((ft) => params.append('file_type', ft));
  }
  if (filters.processing_status) {
    filters.processing_status.forEach((status) =>
      params.append('status', status)
    );
  }
  if (filters.embedding_status) {
    filters.embedding_status.forEach((status) =>
      params.append('embedding_status', status)
    );
  }
  if (filters.search_query) {
    params.append('search', filters.search_query);
  }
  if (filters.date_from) {
    params.append('date_from', filters.date_from);
  }
  if (filters.date_to) {
    params.append('date_to', filters.date_to);
  }

  // Sorting
  if (sort) {
    params.append('sort_by', sort.field);
    params.append('sort_order', sort.order);
  }

  return params;
}

// ============================================================================
// Document List & Detail APIs
// ============================================================================

/**
 * Fetch paginated list of documents with optional filtering
 */
export async function fetchDocuments(
  filters: DocumentFilters = {},
  sort?: SortOptions
): Promise<DocumentListResponse> {
  const params = buildQueryParams(filters, sort);
  const url = `${API_BASE_URL}${API_PREFIX}/documents?${params}`;

  const response = await fetch(url, {
    method: 'GET',
    headers: { 'Content-Type': 'application/json' },
  });

  return handleResponse<DocumentListResponse>(response);
}

/**
 * Fetch detailed information for a single document
 * Includes chunks, extracted texts, and processing jobs
 */
export async function fetchDocumentById(
  documentId: number,
  includeChunks: boolean = false
): Promise<DocumentDetailResponse> {
  const params = new URLSearchParams();
  if (includeChunks) params.append('include_chunks', 'true');

  const url = `${API_BASE_URL}${API_PREFIX}/documents/${documentId}?${params}`;

  const response = await fetch(url, {
    method: 'GET',
    headers: { 'Content-Type': 'application/json' },
  });

  return handleResponse<DocumentDetailResponse>(response);
}

/**
 * Fetch all document chunks for a document
 */
export async function fetchDocumentChunks(
  documentId: number,
  page: number = 1,
  pageSize: number = 50
): Promise<ChunkListResponse> {
  const params = new URLSearchParams({
    page: page.toString(),
    page_size: pageSize.toString(),
  });

  const url = `${API_BASE_URL}${API_PREFIX}/documents/${documentId}/chunks?${params}`;

  const response = await fetch(url, {
    method: 'GET',
    headers: { 'Content-Type': 'application/json' },
  });

  return handleResponse<ChunkListResponse>(response);
}

/**
 * Fetch text preview from extracted_texts
 */
export async function fetchDocumentTextPreview(
  documentId: number,
  maxPages: number = 5,
  previewLength: number = 1000
): Promise<TextPreviewResponse> {
  const params = new URLSearchParams({
    max_pages: maxPages.toString(),
    preview_length: previewLength.toString(),
  });

  const url = `${API_BASE_URL}${API_PREFIX}/documents/${documentId}/text-preview?${params}`;

  const response = await fetch(url, {
    method: 'GET',
    headers: { 'Content-Type': 'application/json' },
  });

  return handleResponse<TextPreviewResponse>(response);
}

/**
 * Fetch embedding statistics for a document
 */
export async function fetchEmbeddingStatistics(
  documentId: number
): Promise<EmbeddingStatistics> {
  const url = `${API_BASE_URL}${API_PREFIX}/documents/${documentId}/embeddings/stats`;

  const response = await fetch(url, {
    method: 'GET',
    headers: { 'Content-Type': 'application/json' },
  });

  return handleResponse<EmbeddingStatistics>(response);
}

// ============================================================================
// Document Actions
// ============================================================================

/**
 * Delete a document
 */
export async function deleteDocument(documentId: number): Promise<void> {
  const url = `${API_BASE_URL}${API_PREFIX}/documents/${documentId}`;

  const response = await fetch(url, {
    method: 'DELETE',
    headers: { 'Content-Type': 'application/json' },
  });

  await handleResponse<{ message: string }>(response);
}

/**
 * Regenerate embeddings for a document
 */
export async function regenerateEmbeddings(
  documentId: number
): Promise<{ job_id: number }> {
  const url = `${API_BASE_URL}${API_PREFIX}/documents/${documentId}/embeddings/regenerate`;

  const response = await fetch(url, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
  });

  return handleResponse<{ job_id: number }>(response);
}

/**
 * Reprocess a document (parse + embed)
 */
export async function reprocessDocument(
  documentId: number
): Promise<{ job_id: number }> {
  const url = `${API_BASE_URL}${API_PREFIX}/documents/${documentId}/reprocess`;

  const response = await fetch(url, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
  });

  return handleResponse<{ job_id: number }>(response);
}

// ============================================================================
// Utility Functions
// ============================================================================

/**
 * Build document detail URL for navigation
 */
export function getDocumentDetailUrl(documentId: number): string {
  return `/documents/${documentId}`;
}

/**
 * Build documents list URL with filters
 */
export function getDocumentsListUrl(filters?: DocumentFilters): string {
  if (!filters || Object.keys(filters).length === 0) {
    return '/documents';
  }

  const params = buildQueryParams(filters);
  return `/documents?${params}`;
}
