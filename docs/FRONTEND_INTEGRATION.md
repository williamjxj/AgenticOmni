

# Frontend Integration Guide

Complete guide for integrating the AgenticOmni document processing API with your frontend application.

**Version**: 0.2.0  
**Last Updated**: 2026-01-09

---

## Table of Contents

1. [API Overview](#api-overview)
2. [Authentication](#authentication)
3. [Document Upload](#document-upload)
4. [TypeScript API Client](#typescript-api-client)
5. [React Components](#react-components)
6. [Error Handling](#error-handling)
7. [Progress Tracking](#progress-tracking)
8. [Best Practices](#best-practices)

---

## API Overview

### Base URL

```typescript
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';
```

### Available Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/documents/upload` | POST | Single file upload |
| `/documents/batch-upload` | POST | Batch upload (1-10 files) |
| `/documents/upload/resumable` | POST | Init resumable upload |
| `/documents/upload/resumable/{id}` | PATCH | Upload chunk |
| `/documents/upload/resumable/{id}` | GET | Get progress |
| `/documents/upload/resumable/{id}` | DELETE | Cancel upload |
| `/documents` | GET | List documents |
| `/documents/{id}` | GET | Get document details |
| `/processing/jobs/{id}` | GET | Get job status |
| `/processing/jobs/{id}/retry` | POST | Retry failed job |
| `/processing/jobs/{id}/cancel` | POST | Cancel job |
| `/health` | GET | Health check |
| `/metrics` | GET | System metrics |

---

## Authentication

Currently, the API uses tenant_id and user_id for multi-tenancy. JWT authentication can be added later.

```typescript
// Add to API requests
const headers = {
  'Content-Type': 'application/json',
  // JWT token (when implemented)
  // 'Authorization': `Bearer ${token}`,
};
```

---

## Document Upload

### Single File Upload

```typescript
// frontend/lib/api/documents.ts

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

export async function uploadDocument(
  file: File,
  tenantId: number,
  userId: number
): Promise<UploadResponse> {
  const formData = new FormData();
  formData.append('file', file);
  formData.append('tenant_id', tenantId.toString());
  formData.append('user_id', userId.toString());

  const response = await fetch(`${API_BASE_URL}/documents/upload`, {
    method: 'POST',
    body: formData,
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.error?.message || 'Upload failed');
  }

  return response.json();
}
```

### Batch Upload

```typescript
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
}

export async function uploadBatch(
  files: File[],
  tenantId: number,
  userId: number
): Promise<BatchUploadResponse> {
  if (files.length > 10) {
    throw new Error('Maximum 10 files per batch');
  }

  const formData = new FormData();
  files.forEach((file) => {
    formData.append('files', file);
  });
  formData.append('tenant_id', tenantId.toString());
  formData.append('user_id', userId.toString());

  const response = await fetch(`${API_BASE_URL}/documents/batch-upload`, {
    method: 'POST',
    body: formData,
  });

  if (!response.ok) {
    throw new Error('Batch upload failed');
  }

  return response.json();
}
```

### Resumable Upload (Large Files)

```typescript
export class ResumableUploader {
  private sessionId: string | null = null;
  private chunkSize: number = 10_000_000; // 10MB

  async initSession(
    file: File,
    tenantId: number,
    userId: number
  ): Promise<string> {
    const response = await fetch(`${API_BASE_URL}/documents/upload/resumable`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        filename: file.name,
        file_size: file.size,
        tenant_id: tenantId,
        user_id: userId,
        chunk_size: this.chunkSize,
      }),
    });

    const data = await response.json();
    this.sessionId = data.session_id;
    return this.sessionId;
  }

  async uploadChunk(
    file: File,
    chunkNumber: number,
    onProgress?: (percent: number) => void
  ): Promise<void> {
    if (!this.sessionId) throw new Error('Session not initialized');

    const start = chunkNumber * this.chunkSize;
    const end = Math.min(start + this.chunkSize, file.size);
    const chunk = file.slice(start, end);

    const response = await fetch(
      `${API_BASE_URL}/documents/upload/resumable/${this.sessionId}`,
      {
        method: 'PATCH',
        headers: {
          'Content-Range': `bytes ${start}-${end - 1}/${file.size}`,
          'Content-Type': 'application/octet-stream',
        },
        body: chunk,
      }
    );

    const data = await response.json();
    if (onProgress) {
      onProgress(data.progress_percent);
    }
  }

  async upload(
    file: File,
    tenantId: number,
    userId: number,
    onProgress?: (percent: number) => void
  ): Promise<void> {
    await this.initSession(file, tenantId, userId);

    const totalChunks = Math.ceil(file.size / this.chunkSize);

    for (let i = 0; i < totalChunks; i++) {
      await this.uploadChunk(file, i, onProgress);
    }
  }
}
```

---

## TypeScript API Client

Complete API client with error handling:

```typescript
// frontend/lib/api/client.ts

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

export class ApiClient {
  private baseUrl: string;
  private tenantId: number;
  private userId: number;

  constructor(tenantId: number, userId: number) {
    this.baseUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';
    this.tenantId = tenantId;
    this.userId = userId;
  }

  async uploadDocument(file: File): Promise<UploadResponse> {
    return uploadDocument(file, this.tenantId, this.userId);
  }

  async uploadBatch(files: File[]): Promise<BatchUploadResponse> {
    return uploadBatch(files, this.tenantId, this.userId);
  }

  async getDocument(documentId: number): Promise<Document> {
    const response = await fetch(
      `${this.baseUrl}/documents/${documentId}`,
      {
        headers: { 'Content-Type': 'application/json' },
      }
    );

    if (!response.ok) {
      throw new ApiError(
        response.status,
        'document_not_found',
        'Document not found'
      );
    }

    return response.json();
  }

  async listDocuments(
    page: number = 1,
    limit: number = 20
  ): Promise<{ documents: Document[]; total: number }> {
    const params = new URLSearchParams({
      tenant_id: this.tenantId.toString(),
      page: page.toString(),
      limit: limit.toString(),
    });

    const response = await fetch(
      `${this.baseUrl}/documents?${params}`,
      {
        headers: { 'Content-Type': 'application/json' },
      }
    );

    return response.json();
  }

  async getJobStatus(jobId: number): Promise<JobStatus> {
    const response = await fetch(
      `${this.baseUrl}/processing/jobs/${jobId}`,
      {
        headers: { 'Content-Type': 'application/json' },
      }
    );

    return response.json();
  }

  async retryJob(jobId: number): Promise<void> {
    const response = await fetch(
      `${this.baseUrl}/processing/jobs/${jobId}/retry`,
      {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
      }
    );

    if (!response.ok) {
      throw new ApiError(
        response.status,
        'retry_failed',
        'Failed to retry job'
      );
    }
  }
}
```

---

## React Components

### Upload Button Component

```typescript
// frontend/components/upload-button.tsx

'use client';

import { useState } from 'react';
import { uploadDocument } from '@/lib/api/documents';
import { Button } from '@/components/ui/button';
import { Loader2 } from 'lucide-react';

export function UploadButton() {
  const [isUploading, setIsUploading] = useState(false);

  const handleUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setIsUploading(true);
    try {
      const result = await uploadDocument(file, 1, 1); // Replace with actual IDs
      console.log('Upload successful:', result);
      // Show success message
    } catch (error) {
      console.error('Upload failed:', error);
      // Show error message
    } finally {
      setIsUploading(false);
    }
  };

  return (
    <div>
      <input
        type="file"
        id="file-upload"
        className="hidden"
        onChange={handleUpload}
        accept=".pdf,.docx,.txt"
      />
      <Button
        asChild
        disabled={isUploading}
      >
        <label htmlFor="file-upload">
          {isUploading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
          {isUploading ? 'Uploading...' : 'Upload Document'}
        </label>
      </Button>
    </div>
  );
}
```

### Progress Tracker Component

```typescript
// frontend/components/upload-progress.tsx

'use client';

import { useEffect, useState } from 'react';
import { getJobStatus, JobStatus } from '@/lib/api/documents';
import { Progress } from '@/components/ui/progress';

interface UploadProgressProps {
  jobId: number;
  onComplete?: () => void;
}

export function UploadProgress({ jobId, onComplete }: UploadProgressProps) {
  const [status, setStatus] = useState<JobStatus | null>(null);

  useEffect(() => {
    let interval: NodeJS.Timeout;

    const fetchStatus = async () => {
      const jobStatus = await getJobStatus(jobId);
      setStatus(jobStatus);

      if (jobStatus.status === 'completed') {
        clearInterval(interval);
        onComplete?.();
      }
    };

    fetchStatus();
    interval = setInterval(fetchStatus, 2000); // Poll every 2 seconds

    return () => clearInterval(interval);
  }, [jobId, onComplete]);

  if (!status) return <div>Loading...</div>;

  return (
    <div className="space-y-2">
      <div className="flex justify-between text-sm">
        <span>Processing...</span>
        <span>{status.progress_percent}%</span>
      </div>
      <Progress value={status.progress_percent} />
      <p className="text-xs text-muted-foreground">
        Status: {status.status}
      </p>
    </div>
  );
}
```

---

## Error Handling

```typescript
// frontend/lib/errors.ts

export function handleApiError(error: any): string {
  if (error instanceof ApiError) {
    switch (error.errorType) {
      case 'file_too_large':
        return 'File exceeds maximum size of 50MB';
      case 'file_type_not_allowed':
        return 'File type not supported. Please upload PDF, DOCX, or TXT files';
      case 'quota_exceeded':
        return 'Storage quota exceeded. Please delete some documents';
      default:
        return error.message;
    }
  }

  return 'An unexpected error occurred';
}
```

---

## Progress Tracking

### Real-time Job Status

```typescript
// Poll job status every 2 seconds
const pollJobStatus = async (jobId: number): Promise<void> => {
  const interval = setInterval(async () => {
    const status = await getJobStatus(jobId);
    
    console.log(`Progress: ${status.progress_percent}%`);
    
    if (status.status === 'completed') {
      clearInterval(interval);
      console.log('Processing complete!');
    } else if (status.status === 'failed') {
      clearInterval(interval);
      console.error('Processing failed');
    }
  }, 2000);
};
```

---

## Best Practices

### 1. File Validation

```typescript
const validateFile = (file: File): boolean => {
  const maxSize = 50 * 1024 * 1024; // 50MB
  const allowedTypes = ['application/pdf', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document', 'text/plain'];

  if (file.size > maxSize) {
    throw new Error('File too large');
  }

  if (!allowedTypes.includes(file.type)) {
    throw new Error('File type not allowed');
  }

  return true;
};
```

### 2. Use Resumable Upload for Large Files

```typescript
const uploadFile = async (file: File) => {
  if (file.size > 50 * 1024 * 1024) {
    // Use resumable upload for files > 50MB
    const uploader = new ResumableUploader();
    await uploader.upload(file, tenantId, userId, (percent) => {
      console.log(`Progress: ${percent}%`);
    });
  } else {
    // Use regular upload for smaller files
    await uploadDocument(file, tenantId, userId);
  }
};
```

### 3. Handle Network Errors

```typescript
const uploadWithRetry = async (
  file: File,
  maxRetries: number = 3
): Promise<UploadResponse> => {
  for (let i = 0; i < maxRetries; i++) {
    try {
      return await uploadDocument(file, tenantId, userId);
    } catch (error) {
      if (i === maxRetries - 1) throw error;
      await new Promise(resolve => setTimeout(resolve, 1000 * (i + 1)));
    }
  }
  throw new Error('Upload failed after retries');
};
```

### 4. Optimize User Experience

- Show upload progress
- Allow cancellation
- Display estimated time remaining
- Handle background uploads
- Show success/error notifications
- Auto-retry on failure

---

## Example: Complete Upload Flow

```typescript
// frontend/app/upload/page.tsx

'use client';

import { useState } from 'react';
import { ApiClient } from '@/lib/api/client';
import { UploadButton } from '@/components/upload-button';
import { UploadProgress } from '@/components/upload-progress';

export default function UploadPage() {
  const [jobId, setJobId] = useState<number | null>(null);
  const client = new ApiClient(1, 1);

  const handleUpload = async (file: File) => {
    const result = await client.uploadDocument(file);
    setJobId(result.job_id);
  };

  const handleComplete = () => {
    console.log('Document processing complete!');
    // Redirect or show success message
  };

  return (
    <div className="container mx-auto p-8">
      <h1 className="text-2xl font-bold mb-4">Upload Document</h1>
      
      <UploadButton onUpload={handleUpload} />
      
      {jobId && (
        <div className="mt-8">
          <UploadProgress jobId={jobId} onComplete={handleComplete} />
        </div>
      )}
    </div>
  );
}
```

---

## Testing

### Unit Tests

```typescript
// frontend/__tests__/api/documents.test.ts

import { uploadDocument } from '@/lib/api/documents';

describe('Document Upload API', () => {
  it('uploads a document successfully', async () => {
    const file = new File(['content'], 'test.txt', { type: 'text/plain' });
    const result = await uploadDocument(file, 1, 1);
    
    expect(result.document_id).toBeDefined();
    expect(result.job_id).toBeDefined();
  });
});
```

---

## Next Steps

1. Implement authentication (JWT)
2. Add WebSocket support for real-time updates
3. Implement document viewer
4. Add RAG query interface
5. Build document management dashboard

---

**Questions?** Contact the development team or see [API Documentation](http://localhost:8000/api/v1/docs).

**Last Updated**: 2026-01-09
