'use client';

/**
 * Document Detail Page
 * Feature: 005-view-embedded-docs / User Story 2
 * Displays detailed information about a single document
 */

import { use } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { ArrowLeft, RefreshCw, Download, Trash2 } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { useDocumentDetail } from '@/lib/hooks/useDocuments';
import { DocumentHeader } from '@/components/documents/document-header';
import { ProcessingStatusCard } from '@/components/documents/processing-status-card';
import { EmbeddingStatusCard } from '@/components/documents/embedding-status-card';
import { TextPreview } from '@/components/documents/text-preview';
import { EmbeddingDetailsPanel } from '@/components/documents/embedding-details-panel';
import { DocumentNotFoundState } from '@/components/documents/empty-state';
import { DocumentDetailPageSkeleton } from '@/components/ui/skeleton';
import { getErrorMessage } from '@/lib/utils/error-handling';

interface DocumentDetailPageProps {
  params: Promise<{ id: string }>;
}

/**
 * Document Detail Page Component
 * 
 * Provides:
 * - Document metadata and header
 * - Processing status information
 * - Embedding status and statistics
 * - Text preview
 * - Action buttons (download, delete, reprocess)
 * - Error handling
 */
export default function DocumentDetailPage({ params }: DocumentDetailPageProps) {
  const router = useRouter();
  const { id: documentIdStr } = use(params);
  const documentId = parseInt(documentIdStr, 10);

  // Fetch document details
  const { document, loading, error, refetch } = useDocumentDetail(documentId);

  const handleDownload = () => {
    // TODO: Implement download functionality
    console.log('Download document:', documentId);
  };

  const handleDelete = async () => {
    if (!confirm('Are you sure you want to delete this document? This action cannot be undone.')) {
      return;
    }
    // TODO: Implement delete functionality
    console.log('Delete document:', documentId);
  };

  const handleReprocess = async () => {
    if (!confirm('Reprocess this document? This will re-parse and regenerate embeddings.')) {
      return;
    }
    // TODO: Implement reprocess functionality
    console.log('Reprocess document:', documentId);
  };

  // Loading state
  if (loading) {
    return (
      <div className="min-h-screen bg-slate-50 dark:bg-slate-950">
        <header className="border-b bg-white dark:bg-slate-900">
          <div className="container mx-auto px-4 py-4">
            <div className="flex items-center gap-4">
              <Button variant="ghost" size="sm" asChild>
                <Link href="/documents">
                  <ArrowLeft className="h-4 w-4 mr-2" />
                  Back to Documents
                </Link>
              </Button>
            </div>
          </div>
        </header>
        <main className="container mx-auto px-4 py-8">
          <div className="max-w-5xl mx-auto">
            <DocumentDetailPageSkeleton />
          </div>
        </main>
      </div>
    );
  }

  // Error or not found state
  if (error || !document) {
    return (
      <div className="min-h-screen bg-slate-50 dark:bg-slate-950">
        <header className="border-b bg-white dark:bg-slate-900">
          <div className="container mx-auto px-4 py-4">
            <div className="flex items-center gap-4">
              <Button variant="ghost" size="sm" asChild>
                <Link href="/documents">
                  <ArrowLeft className="h-4 w-4 mr-2" />
                  Back to Documents
                </Link>
              </Button>
            </div>
          </div>
        </header>
        <main className="container mx-auto px-4 py-8">
          <div className="max-w-5xl mx-auto">
            {error ? (
              <div className="bg-red-50 dark:bg-red-950 border border-red-200 dark:border-red-800 rounded-lg p-6 text-center">
                <h3 className="text-lg font-semibold text-red-900 dark:text-red-100 mb-2">
                  Error Loading Document
                </h3>
                <p className="text-red-700 dark:text-red-300 mb-4">
                  {getErrorMessage(error)}
                </p>
                <Button onClick={refetch} variant="outline">
                  <RefreshCw className="h-4 w-4 mr-2" />
                  Try Again
                </Button>
              </div>
            ) : (
              <DocumentNotFoundState documentId={documentId} />
            )}
          </div>
        </main>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-50 dark:bg-slate-950">
      {/* Header */}
      <header className="sticky top-0 z-10 border-b bg-white dark:bg-slate-900 shadow-sm">
        <div className="container mx-auto px-4 py-4">
          <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
            {/* Navigation */}
            <div className="flex items-center gap-4">
              <Button variant="ghost" size="sm" asChild>
                <Link href="/documents">
                  <ArrowLeft className="h-4 w-4 mr-2" />
                  Back
                </Link>
              </Button>
              <div>
                <h1 className="text-xl sm:text-2xl font-bold text-slate-900 dark:text-slate-100 truncate max-w-md">
                  Document Details
                </h1>
                <p className="text-sm text-slate-600 dark:text-slate-400 mt-0.5">
                  ID: {document.document_id}
                </p>
              </div>
            </div>

            {/* Action buttons */}
            <div className="flex gap-2 w-full sm:w-auto">
              <Button
                variant="outline"
                size="sm"
                onClick={refetch}
                className="flex-1 sm:flex-none"
              >
                <RefreshCw className="h-4 w-4 mr-2" />
                Refresh
              </Button>
              <Button
                variant="outline"
                size="sm"
                onClick={handleDownload}
                className="flex-1 sm:flex-none"
              >
                <Download className="h-4 w-4 mr-2" />
                Download
              </Button>
              <Button
                variant="outline"
                size="sm"
                onClick={handleDelete}
                className="flex-1 sm:flex-none text-red-600 hover:text-red-700 hover:bg-red-50 dark:hover:bg-red-950"
              >
                <Trash2 className="h-4 w-4 mr-2" />
                Delete
              </Button>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="container mx-auto px-4 py-6 sm:py-8">
        <div className="max-w-5xl mx-auto space-y-6">
          {/* Document Header */}
          <DocumentHeader document={document} />

          {/* Status Cards Row */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <ProcessingStatusCard document={document} onReprocess={handleReprocess} />
            <EmbeddingStatusCard document={document} onRegenerate={handleReprocess} />
          </div>

          {/* Text Preview */}
          {document.processing_status === 'parsed' && (
            <TextPreview documentId={document.document_id} />
          )}

          {/* Embedding Details */}
          {document.embedding_status && document.embedding_status !== 'not_started' && (
            <EmbeddingDetailsPanel document={document} />
          )}

          {/* Additional Information */}
          {document.document_metadata && Object.keys(document.document_metadata).length > 0 && (
            <div className="border rounded-lg p-6 bg-white dark:bg-slate-900">
              <h3 className="text-lg font-semibold mb-4 text-slate-900 dark:text-slate-100">
                Additional Metadata
              </h3>
              <dl className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                {Object.entries(document.document_metadata).map(([key, value]) => (
                  <div key={key}>
                    <dt className="text-sm text-slate-600 dark:text-slate-400 mb-1">
                      {key.replace(/_/g, ' ').replace(/\b\w/g, (l) => l.toUpperCase())}
                    </dt>
                    <dd className="text-sm font-medium text-slate-900 dark:text-slate-100">
                      {typeof value === 'object' ? JSON.stringify(value, null, 2) : String(value)}
                    </dd>
                  </div>
                ))}
              </dl>
            </div>
          )}
        </div>
      </main>
    </div>
  );
}
