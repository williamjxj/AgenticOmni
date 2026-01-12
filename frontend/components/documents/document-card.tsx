/**
 * Document Card Component
 * Displays a single document with metadata and actions
 * Feature: 005-view-embedded-docs / User Story 1
 */

import Link from 'next/link';
import { Download, FileText } from 'lucide-react';
import { Document } from '@/lib/types/document';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import { StatusBadge } from './status-badge';
import { FileTypeIcon } from './file-type-icon';

interface DocumentCardProps {
  document: Document;
  onDownload?: (documentId: number) => void;
  onClick?: (documentId: number) => void;
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
 * Format date for display
 */
function formatDate(dateString: string): string {
  return new Date(dateString).toLocaleString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  });
}

/**
 * Document Card Component
 * 
 * @example
 * ```tsx
 * <DocumentCard 
 *   document={document} 
 *   onDownload={(id) => handleDownload(id)}
 * />
 * ```
 */
export function DocumentCard({
  document,
  onDownload,
  onClick,
}: DocumentCardProps) {
  const handleCardClick = () => {
    if (onClick) {
      onClick(document.document_id);
    }
  };

  const handleDownload = (e: React.MouseEvent) => {
    e.stopPropagation();
    if (onDownload) {
      onDownload(document.document_id);
    }
  };

  return (
    <Card 
      className="hover:shadow-md transition-shadow cursor-pointer"
      onClick={handleCardClick}
    >
      <CardContent className="p-6">
        <div className="flex items-start justify-between gap-4">
          {/* Left section: Icon + Metadata */}
          <div className="flex gap-4 flex-1 min-w-0">
            {/* File icon */}
            <div className="flex-shrink-0 mt-1">
              <FileTypeIcon fileType={document.file_type} size="lg" />
            </div>

            {/* Document metadata */}
            <div className="flex-1 min-w-0 space-y-2">
              {/* Filename - clickable */}
              <Link 
                href={`/documents/${document.document_id}`}
                onClick={(e) => e.stopPropagation()}
              >
                <h3 className="font-semibold truncate text-slate-900 dark:text-slate-100 hover:text-blue-600 dark:hover:text-blue-400 transition-colors">
                  {document.original_filename}
                </h3>
              </Link>

              {/* Metadata row */}
              <div className="flex flex-wrap gap-3 text-sm text-slate-600 dark:text-slate-400">
                <span className="whitespace-nowrap">
                  ID: {document.document_id}
                </span>
                <span className="text-slate-300 dark:text-slate-700">•</span>
                <span className="whitespace-nowrap">
                  {formatFileSize(document.file_size)}
                </span>
                <span className="text-slate-300 dark:text-slate-700">•</span>
                <span className="whitespace-nowrap">
                  {document.file_type.toUpperCase()}
                </span>
                {document.page_count && (
                  <>
                    <span className="text-slate-300 dark:text-slate-700">•</span>
                    <span className="whitespace-nowrap">
                      {document.page_count} {document.page_count === 1 ? 'page' : 'pages'}
                    </span>
                  </>
                )}
                {document.language_detected && (
                  <>
                    <span className="text-slate-300 dark:text-slate-700">•</span>
                    <span className="whitespace-nowrap">
                      {document.language_detected}
                    </span>
                  </>
                )}
              </div>

              {/* Upload timestamp */}
              <p className="text-xs text-slate-500 dark:text-slate-500">
                Uploaded {formatDate(document.uploaded_at)}
              </p>

              {/* Embedding status (if available) */}
              {document.embedding_status && document.embedding_status !== 'not_started' && (
                <div className="text-xs">
                  <span className="text-slate-500 dark:text-slate-500">
                    Embedding: 
                  </span>
                  <StatusBadge 
                    status={document.embedding_status} 
                    type="embedding" 
                    size="sm"
                    className="ml-1"
                  />
                </div>
              )}
            </div>
          </div>

          {/* Right section: Status + Actions */}
          <div className="flex items-center gap-3 flex-shrink-0">
            {/* Processing status badge */}
            <StatusBadge 
              status={document.processing_status} 
              type="processing"
            />

            {/* Download button */}
            <Button
              size="sm"
              variant="outline"
              onClick={handleDownload}
              title="Download document"
              className="h-8 w-8 p-0"
            >
              <Download className="h-4 w-4" />
            </Button>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
