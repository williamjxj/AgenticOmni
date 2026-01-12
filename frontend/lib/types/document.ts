/**
 * Comprehensive TypeScript types for document entities
 * Feature: 005-view-embedded-docs
 */

// ============================================================================
// Core Document Types
// ============================================================================

export interface Document {
  document_id: number;
  filename: string;
  original_filename: string;
  file_type: string;
  mime_type: string;
  file_size: number;
  storage_path?: string;
  content_hash: string;
  
  // Processing status
  processing_status: ProcessingStatus;
  ocr_status?: OCRStatus;
  ocr_confidence?: number;
  embedding_status?: EmbeddingStatus;
  
  // Metadata
  language_detected?: string;
  page_count?: number;
  has_scanned_content?: boolean;
  ocr_engine_used?: string;
  document_metadata?: Record<string, any>;
  
  // Timestamps
  created_at: string;
  updated_at: string;
  uploaded_at: string;
  
  // Relationships (when fetching with joins)
  chunks?: DocumentChunk[];
  extracted_texts?: ExtractedText[];
  processing_jobs?: ProcessingJob[];
}

// ============================================================================
// Status Enums
// ============================================================================

export type ProcessingStatus = 
  | 'uploaded' 
  | 'parsing' 
  | 'parsed' 
  | 'failed'
  | 'pending';

export type OCRStatus = 
  | 'not_started' 
  | 'in_progress' 
  | 'completed' 
  | 'failed';

export type EmbeddingStatus = 
  | 'not_started' 
  | 'in_progress' 
  | 'completed' 
  | 'failed';

export type JobStatus = 
  | 'pending' 
  | 'processing' 
  | 'completed' 
  | 'failed' 
  | 'retrying';

// ============================================================================
// Document Chunk Types
// ============================================================================

export interface DocumentChunk {
  chunk_id: number;
  document_id: number;
  content_text: string;
  embedding_vector: number[] | null;
  chunk_order: number;
  chunk_sequence: number;
  
  // Chunk metadata
  chunk_type: ChunkType;
  token_count?: number;
  start_page?: number;
  end_page?: number;
  char_offset_start?: number;
  char_offset_end?: number;
  section_heading?: string;
  parent_heading?: string;
  
  // Embedding metadata
  embedding_model?: string;
  embedding_generated_at?: string;
  
  created_at: string;
}

export type ChunkType = 
  | 'text' 
  | 'table' 
  | 'list' 
  | 'heading' 
  | 'code';

// ============================================================================
// Extracted Text Types
// ============================================================================

export interface ExtractedText {
  extracted_text_id: number;
  document_id: number;
  page_number: number;
  extraction_method: ExtractionMethod;
  text_content: string;
  confidence_score?: number;
  character_count: number;
  created_at: string;
}

export type ExtractionMethod = 
  | 'native' 
  | 'ocr_paddleocr' 
  | 'ocr_tesseract';

// ============================================================================
// Processing Job Types
// ============================================================================

export interface ProcessingJob {
  job_id: number;
  document_id: number;
  job_type: JobType;
  status: JobStatus;
  
  // Progress tracking
  progress_percent?: number;
  retry_count: number;
  max_retries: number;
  
  // Timestamps
  started_at?: string;
  completed_at?: string;
  created_at: string;
  
  // Error handling
  error_category?: ErrorCategory;
  error_message?: string;
}

export type JobType = 
  | 'parse_document' 
  | 'ocr_extraction' 
  | 'embedding_generation' 
  | 'batch_processing';

export type ErrorCategory = 
  | 'transient' 
  | 'permanent' 
  | 'resource_exhaustion';

// ============================================================================
// API Response Types
// ============================================================================

export interface DocumentListResponse {
  documents: Document[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

export interface DocumentDetailResponse extends Document {
  chunks: DocumentChunk[];
  extracted_texts: ExtractedText[];
  processing_jobs: ProcessingJob[];
  chunk_count: number;
  embedding_count: number;
}

export interface ChunkListResponse {
  chunks: DocumentChunk[];
  total: number;
  document_id: number;
  embedding_model?: string;
  vector_dimensions?: number;
  avg_chunk_size?: number;
}

export interface TextPreviewResponse {
  document_id: number;
  pages: {
    page_number: number;
    extraction_method: ExtractionMethod;
    confidence_score?: number;
    text_preview: string;
  }[];
  total_characters: number;
}

// ============================================================================
// Embedding Statistics Types
// ============================================================================

export interface EmbeddingStatistics {
  embedding_model: string;
  vector_dimensions: number;
  total_chunks: number;
  chunks_with_embeddings: number;
  avg_chunk_size: number;
  min_chunk_size: number;
  max_chunk_size: number;
  embedding_coverage: number; // percentage
}

// ============================================================================
// Filter & Search Types
// ============================================================================

export interface DocumentFilters {
  file_type?: string[];
  processing_status?: ProcessingStatus[];
  embedding_status?: EmbeddingStatus[];
  ocr_status?: OCRStatus[];
  date_from?: string;
  date_to?: string;
  search_query?: string;
  page?: number;
  page_size?: number;
}

export interface SortOptions {
  field: 'created_at' | 'updated_at' | 'filename' | 'file_size';
  order: 'asc' | 'desc';
}

// ============================================================================
// UI Helper Types
// ============================================================================

export interface StatusBadge {
  label: string;
  color: string;
  icon?: string;
}

export interface FileTypeInfo {
  type: string;
  icon: string;
  color: string;
  label: string;
}

// ============================================================================
// Error Types
// ============================================================================

export class DocumentError extends Error {
  constructor(
    message: string,
    public code?: string,
    public details?: Record<string, any>
  ) {
    super(message);
    this.name = 'DocumentError';
  }
}

export class ApiError extends Error {
  constructor(
    public statusCode: number,
    public errorType: string,
    message: string,
    public details?: Record<string, any>
  ) {
    super(message);
    this.name = 'ApiError';
  }
}
