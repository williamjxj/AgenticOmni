/**
 * API Client for AgenticOmni Backend
 */

import {
  ApiError,
  BatchUploadResponse,
  ChunkUploadProgress,
  Document,
  JobStatus,
  ResumableUploadSession,
  UploadResponse,
} from './types';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export class ApiClient {
  private baseUrl: string;
  private tenantId: number;
  private userId: number;

  constructor(tenantId: number = 1, userId: number = 1) {
    // Add /api/v1 prefix to base URL
    this.baseUrl = `${API_BASE_URL}/api/v1`;
    this.tenantId = tenantId;
    this.userId = userId;
  }

  private async handleResponse<T>(response: Response): Promise<T> {
    if (!response.ok) {
      let errorMessage = `HTTP ${response.status}`;
      let errorType = 'unknown';
      
      try {
        const errorData = await response.json();
        errorType = errorData.error?.type || errorData.detail?.type || 'unknown';
        errorMessage = errorData.error?.message || errorData.detail || errorData.message || errorMessage;
      } catch (e) {
        // If JSON parsing fails, try text
        try {
          const errorText = await response.text();
          if (errorText) errorMessage = errorText;
        } catch {
          // Keep default error message
        }
      }
      
      throw new ApiError(response.status, errorType, errorMessage);
    }
    
    return response.json();
  }

  // ========================================================================
  // Document Upload
  // ========================================================================

  async uploadDocument(file: File): Promise<UploadResponse> {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('tenant_id', this.tenantId.toString());
    formData.append('user_id', this.userId.toString());

    const response = await fetch(`${this.baseUrl}/documents/upload`, {
      method: 'POST',
      body: formData,
    });

    return this.handleResponse<UploadResponse>(response);
  }

  async uploadBatch(files: File[]): Promise<BatchUploadResponse> {
    if (files.length > 10) {
      throw new Error('Maximum 10 files per batch');
    }

    const formData = new FormData();
    files.forEach((file) => {
      formData.append('files', file);
    });
    formData.append('tenant_id', this.tenantId.toString());
    formData.append('user_id', this.userId.toString());

    const response = await fetch(`${this.baseUrl}/documents/batch-upload`, {
      method: 'POST',
      body: formData,
    });

    return this.handleResponse<BatchUploadResponse>(response);
  }

  // ========================================================================
  // Resumable Upload
  // ========================================================================

  async initResumableUpload(
    filename: string,
    fileSize: number,
    chunkSize: number = 10_000_000
  ): Promise<ResumableUploadSession> {
    const response = await fetch(`${this.baseUrl}/documents/upload/resumable`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        filename,
        file_size: fileSize,
        tenant_id: this.tenantId,
        user_id: this.userId,
        chunk_size: chunkSize,
      }),
    });

    return this.handleResponse<ResumableUploadSession>(response);
  }

  async uploadChunk(
    sessionId: string,
    chunk: Blob,
    start: number,
    end: number,
    totalSize: number
  ): Promise<ChunkUploadProgress> {
    const response = await fetch(
      `${this.baseUrl}/documents/upload/resumable/${sessionId}`,
      {
        method: 'PATCH',
        headers: {
          'Content-Range': `bytes ${start}-${end - 1}/${totalSize}`,
          'Content-Type': 'application/octet-stream',
        },
        body: chunk,
      }
    );

    return this.handleResponse<ChunkUploadProgress>(response);
  }

  async getResumableProgress(sessionId: string): Promise<ResumableUploadSession> {
    const response = await fetch(
      `${this.baseUrl}/documents/upload/resumable/${sessionId}`,
      {
        method: 'GET',
        headers: { 'Content-Type': 'application/json' },
      }
    );

    return this.handleResponse<ResumableUploadSession>(response);
  }

  async cancelResumableUpload(sessionId: string): Promise<void> {
    const response = await fetch(
      `${this.baseUrl}/documents/upload/resumable/${sessionId}`,
      {
        method: 'DELETE',
        headers: { 'Content-Type': 'application/json' },
      }
    );

    await this.handleResponse<{ status: string }>(response);
  }

  // ========================================================================
  // Document Management
  // ========================================================================

  async getDocument(documentId: number): Promise<Document> {
    const response = await fetch(`${this.baseUrl}/documents/${documentId}`, {
      headers: { 'Content-Type': 'application/json' },
    });

    return this.handleResponse<Document>(response);
  }

  async listDocuments(
    page: number = 1,
    limit: number = 20,
    statusFilter?: string,
    fileType?: string
  ): Promise<{ documents: Document[]; total: number; page: number; total_pages: number }> {
    const params = new URLSearchParams({
      tenant_id: this.tenantId.toString(),
      page: page.toString(),
      limit: limit.toString(),
    });

    if (statusFilter) params.append('status', statusFilter);
    if (fileType) params.append('file_type', fileType);

    const response = await fetch(`${this.baseUrl}/documents?${params}`, {
      headers: { 'Content-Type': 'application/json' },
    });

    return this.handleResponse(response);
  }

  // ========================================================================
  // Job Management
  // ========================================================================

  async getJobStatus(jobId: number): Promise<JobStatus> {
    const response = await fetch(`${this.baseUrl}/processing/jobs/${jobId}`, {
      headers: { 'Content-Type': 'application/json' },
    });

    return this.handleResponse<JobStatus>(response);
  }

  async retryJob(jobId: number): Promise<void> {
    const response = await fetch(
      `${this.baseUrl}/processing/jobs/${jobId}/retry`,
      {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
      }
    );

    await this.handleResponse<{ message: string }>(response);
  }

  async cancelJob(jobId: number): Promise<void> {
    const response = await fetch(
      `${this.baseUrl}/processing/jobs/${jobId}/cancel`,
      {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
      }
    );

    await this.handleResponse<{ message: string }>(response);
  }

  // ========================================================================
  // Health Check
  // ========================================================================

  async healthCheck(): Promise<{ status: string; database: string }> {
    const response = await fetch(`${this.baseUrl}/health`, {
      headers: { 'Content-Type': 'application/json' },
    });

    return this.handleResponse(response);
  }
}

// Export singleton instance
export const apiClient = new ApiClient();
