/**
 * Document List Component
 * Displays a list of document cards with loading and empty states
 * Feature: 005-view-embedded-docs / User Story 1
 */

import { Document } from '@/lib/types/document';
import { DocumentCard } from './document-card';
import { EmptyState } from './empty-state';
import { DocumentListSkeleton } from '@/components/ui/skeleton';

interface DocumentListProps {
  documents: Document[];
  loading?: boolean;
  error?: string | null;
  emptyVariant?: 'no-documents' | 'no-results' | 'no-filtered-results';
  onDocumentClick?: (documentId: number) => void;
  onDocumentDownload?: (documentId: number) => void;
  onRetry?: () => void;
  className?: string;
}

/**
 * Document List Component
 * 
 * Handles rendering of document list with:
 * - Loading state (skeleton)
 * - Empty state (no documents/results)
 * - Error state
 * - Normal state (document cards)
 * 
 * @example
 * ```tsx
 * <DocumentList 
 *   documents={documents}
 *   loading={loading}
 *   error={error}
 *   onDocumentClick={(id) => router.push(`/documents/${id}`)}
 * />
 * ```
 */
export function DocumentList({
  documents,
  loading = false,
  error = null,
  emptyVariant = 'no-documents',
  onDocumentClick,
  onDocumentDownload,
  onRetry,
  className,
}: DocumentListProps) {
  // Loading state
  if (loading) {
    return <DocumentListSkeleton count={5} />;
  }

  // Error state
  if (error) {
    return (
      <EmptyState
        variant="error"
        title="Unable to load documents"
        description={error}
        actionLabel="Try Again"
        onAction={onRetry}
        className={className}
      />
    );
  }

  // Empty state
  if (!documents || documents.length === 0) {
    return <EmptyState variant={emptyVariant} className={className} />;
  }

  // Normal state - render document cards
  return (
    <div className={className}>
      <div className="space-y-4">
        {documents.map((document) => (
          <DocumentCard
            key={document.document_id}
            document={document}
            onClick={onDocumentClick}
            onDownload={onDocumentDownload}
          />
        ))}
      </div>
    </div>
  );
}

/**
 * Document Grid Component
 * Alternative layout that displays documents in a grid
 * 
 * @example
 * ```tsx
 * <DocumentGrid documents={documents} columns={3} />
 * ```
 */
export function DocumentGrid({
  documents,
  loading = false,
  error = null,
  columns = 2,
  emptyVariant = 'no-documents',
  onDocumentClick,
  onDocumentDownload,
  onRetry,
  className,
}: DocumentListProps & { columns?: 1 | 2 | 3 | 4 }) {
  // Loading state
  if (loading) {
    return <DocumentListSkeleton count={6} />;
  }

  // Error state
  if (error) {
    return (
      <EmptyState
        variant="error"
        title="Unable to load documents"
        description={error}
        actionLabel="Try Again"
        onAction={onRetry}
        className={className}
      />
    );
  }

  // Empty state
  if (!documents || documents.length === 0) {
    return <EmptyState variant={emptyVariant} className={className} />;
  }

  const gridCols = {
    1: 'grid-cols-1',
    2: 'grid-cols-1 md:grid-cols-2',
    3: 'grid-cols-1 md:grid-cols-2 lg:grid-cols-3',
    4: 'grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4',
  };

  return (
    <div className={className}>
      <div className={`grid ${gridCols[columns]} gap-4`}>
        {documents.map((document) => (
          <DocumentCard
            key={document.document_id}
            document={document}
            onClick={onDocumentClick}
            onDownload={onDocumentDownload}
          />
        ))}
      </div>
    </div>
  );
}

/**
 * Compact Document List
 * Simplified list view for sidebars or smaller spaces
 */
export function CompactDocumentList({
  documents,
  loading = false,
  onDocumentClick,
  className,
}: Pick<
  DocumentListProps,
  'documents' | 'loading' | 'onDocumentClick' | 'className'
>) {
  if (loading) {
    return <DocumentListSkeleton count={3} />;
  }

  if (!documents || documents.length === 0) {
    return (
      <div className="text-center py-8 text-slate-500 text-sm">
        No documents available
      </div>
    );
  }

  return (
    <div className={className}>
      <ul className="space-y-2">
        {documents.map((document) => (
          <li key={document.document_id}>
            <button
              onClick={() => onDocumentClick?.(document.document_id)}
              className="w-full text-left px-3 py-2 rounded-md hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors"
            >
              <div className="font-medium text-sm truncate text-slate-900 dark:text-slate-100">
                {document.original_filename}
              </div>
              <div className="text-xs text-slate-500 dark:text-slate-500">
                {document.file_type.toUpperCase()} • {document.document_id}
              </div>
            </button>
          </li>
        ))}
      </ul>
    </div>
  );
}
