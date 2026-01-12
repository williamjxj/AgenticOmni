/**
 * Document Header Component
 * Displays document metadata and key information
 * Feature: 005-view-embedded-docs / User Story 2
 */

import { FileTypeLabel } from './file-type-icon';
import { StatusBadge } from './status-badge';
import { formatDate, formatRelativeTime } from '@/lib/utils/date';
import type { Document } from '@/lib/types/document';

interface DocumentHeaderProps {
  document: Document;
}

/**
 * Format file size for display
 */
function formatFileSize(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(2)} KB`;
  if (bytes < 1024 * 1024 * 1024) return `${(bytes / (1024 * 1024)).toFixed(2)} MB`;
  return `${(bytes / (1024 * 1024 * 1024)).toFixed(2)} GB`;
}

/**
 * Document Header Component
 * 
 * Displays:
 * - Filename and file type
 * - Processing status
 * - Key metadata (size, upload date, pages, language)
 * - Content hash
 * 
 * @example
 * ```tsx
 * <DocumentHeader document={document} />
 * ```
 */
export function DocumentHeader({ document }: DocumentHeaderProps) {
  return (
    <div className="border rounded-lg p-6 bg-white dark:bg-slate-900 space-y-6">
      {/* Title Row */}
      <div className="flex flex-col sm:flex-row sm:items-start justify-between gap-4">
        <div className="flex-1 min-w-0 space-y-3">
          {/* Filename */}
          <div>
            <h2 className="text-2xl font-bold text-slate-900 dark:text-slate-100 break-words">
              {document.original_filename}
            </h2>
            {document.filename !== document.original_filename && (
              <p className="text-sm text-slate-500 dark:text-slate-500 mt-1 font-mono">
                Stored as: {document.filename}
              </p>
            )}
          </div>

          {/* File Type and Status */}
          <div className="flex flex-wrap items-center gap-3">
            <FileTypeLabel fileType={document.file_type} size="md" />
            <StatusBadge status={document.processing_status} type="processing" size="md" />
            {document.embedding_status && document.embedding_status !== 'not_started' && (
              <StatusBadge status={document.embedding_status} type="embedding" size="md" />
            )}
          </div>
        </div>
      </div>

      {/* Metadata Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6 pt-4 border-t border-slate-200 dark:border-slate-800">
        {/* File Size */}
        <div>
          <dt className="text-sm font-medium text-slate-600 dark:text-slate-400 mb-1">
            File Size
          </dt>
          <dd className="text-lg font-semibold text-slate-900 dark:text-slate-100">
            {formatFileSize(document.file_size)}
          </dd>
        </div>

        {/* Upload Date */}
        <div>
          <dt className="text-sm font-medium text-slate-600 dark:text-slate-400 mb-1">
            Uploaded
          </dt>
          <dd className="text-lg font-semibold text-slate-900 dark:text-slate-100">
            {formatRelativeTime(document.uploaded_at)}
          </dd>
          <dd className="text-xs text-slate-500 dark:text-slate-500 mt-0.5">
            {formatDate(document.uploaded_at)}
          </dd>
        </div>

        {/* Page Count */}
        {document.page_count !== null && document.page_count !== undefined && (
          <div>
            <dt className="text-sm font-medium text-slate-600 dark:text-slate-400 mb-1">
              Pages
            </dt>
            <dd className="text-lg font-semibold text-slate-900 dark:text-slate-100">
              {document.page_count}
            </dd>
          </div>
        )}

        {/* Language */}
        {document.language_detected && (
          <div>
            <dt className="text-sm font-medium text-slate-600 dark:text-slate-400 mb-1">
              Language
            </dt>
            <dd className="text-lg font-semibold text-slate-900 dark:text-slate-100">
              {document.language_detected.toUpperCase()}
            </dd>
          </div>
        )}

        {/* MIME Type */}
        <div>
          <dt className="text-sm font-medium text-slate-600 dark:text-slate-400 mb-1">
            MIME Type
          </dt>
          <dd className="text-sm font-mono text-slate-700 dark:text-slate-300">
            {document.mime_type}
          </dd>
        </div>

        {/* Created At */}
        <div>
          <dt className="text-sm font-medium text-slate-600 dark:text-slate-400 mb-1">
            Created
          </dt>
          <dd className="text-sm text-slate-700 dark:text-slate-300">
            {formatDate(document.created_at)}
          </dd>
        </div>

        {/* Updated At */}
        <div>
          <dt className="text-sm font-medium text-slate-600 dark:text-slate-400 mb-1">
            Last Updated
          </dt>
          <dd className="text-sm text-slate-700 dark:text-slate-300">
            {formatRelativeTime(document.updated_at)}
          </dd>
        </div>

        {/* Content Hash */}
        <div className="sm:col-span-2 lg:col-span-1">
          <dt className="text-sm font-medium text-slate-600 dark:text-slate-400 mb-1">
            Content Hash
          </dt>
          <dd className="text-xs font-mono text-slate-700 dark:text-slate-300 break-all">
            {document.content_hash.substring(0, 16)}...
          </dd>
        </div>
      </div>

      {/* OCR Information (if applicable) */}
      {document.has_scanned_content && (
        <div className="pt-4 border-t border-slate-200 dark:border-slate-800">
          <h3 className="text-sm font-semibold text-slate-900 dark:text-slate-100 mb-3">
            OCR Information
          </h3>
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
            {document.ocr_status && (
              <div>
                <dt className="text-sm text-slate-600 dark:text-slate-400 mb-1">
                  OCR Status
                </dt>
                <dd>
                  <StatusBadge status={document.ocr_status} type="ocr" size="sm" />
                </dd>
              </div>
            )}
            {document.ocr_engine_used && (
              <div>
                <dt className="text-sm text-slate-600 dark:text-slate-400 mb-1">
                  OCR Engine
                </dt>
                <dd className="text-sm font-medium text-slate-900 dark:text-slate-100">
                  {document.ocr_engine_used}
                </dd>
              </div>
            )}
            {document.ocr_confidence !== null && document.ocr_confidence !== undefined && (
              <div>
                <dt className="text-sm text-slate-600 dark:text-slate-400 mb-1">
                  OCR Confidence
                </dt>
                <dd className="text-sm font-medium text-slate-900 dark:text-slate-100">
                  {(document.ocr_confidence * 100).toFixed(1)}%
                </dd>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}

/**
 * Compact Document Header
 * Simplified version for smaller spaces
 */
export function CompactDocumentHeader({ document }: DocumentHeaderProps) {
  return (
    <div className="border rounded-lg p-4 bg-white dark:bg-slate-900">
      <div className="flex items-start justify-between gap-3">
        <div className="flex-1 min-w-0">
          <h3 className="font-semibold text-slate-900 dark:text-slate-100 truncate">
            {document.original_filename}
          </h3>
          <div className="flex flex-wrap items-center gap-2 mt-2 text-sm text-slate-600 dark:text-slate-400">
            <span>{document.file_type.toUpperCase()}</span>
            <span className="text-slate-300 dark:text-slate-700">•</span>
            <span>{formatFileSize(document.file_size)}</span>
            <span className="text-slate-300 dark:text-slate-700">•</span>
            <span>{formatRelativeTime(document.uploaded_at)}</span>
          </div>
        </div>
        <StatusBadge status={document.processing_status} type="processing" size="sm" />
      </div>
    </div>
  );
}
