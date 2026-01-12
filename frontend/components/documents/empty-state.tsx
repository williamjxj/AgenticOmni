/**
 * Empty State Component
 * Displays friendly message when no documents are available
 * Feature: 005-view-embedded-docs / User Story 1
 */

import Link from 'next/link';
import { FileText, Upload, Search, Filter } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import { cn } from '@/lib/utils';

interface EmptyStateProps {
  variant?: 'no-documents' | 'no-results' | 'no-filtered-results' | 'error';
  title?: string;
  description?: string;
  actionLabel?: string;
  actionHref?: string;
  onAction?: () => void;
  className?: string;
}

/**
 * Get default content based on variant
 */
function getDefaultContent(variant: EmptyStateProps['variant']) {
  switch (variant) {
    case 'no-results':
      return {
        icon: Search,
        title: 'No search results',
        description: 'We couldn\'t find any documents matching your search. Try different keywords.',
        actionLabel: 'Clear Search',
      };
    case 'no-filtered-results':
      return {
        icon: Filter,
        title: 'No matching documents',
        description: 'No documents match the current filters. Try adjusting your filter criteria.',
        actionLabel: 'Clear Filters',
      };
    case 'error':
      return {
        icon: FileText,
        title: 'Unable to load documents',
        description: 'An error occurred while loading documents. Please try again.',
        actionLabel: 'Try Again',
      };
    case 'no-documents':
    default:
      return {
        icon: FileText,
        title: 'No documents yet',
        description: 'Upload your first document to get started with AI-powered document search.',
        actionLabel: 'Upload Document',
        actionHref: '/upload',
      };
  }
}

/**
 * Empty State Component
 * 
 * @example
 * ```tsx
 * <EmptyState variant="no-documents" />
 * <EmptyState 
 *   variant="no-results"
 *   title="Custom title"
 *   onAction={() => clearSearch()}
 * />
 * ```
 */
export function EmptyState({
  variant = 'no-documents',
  title,
  description,
  actionLabel,
  actionHref,
  onAction,
  className,
}: EmptyStateProps) {
  const defaults = getDefaultContent(variant);
  const Icon = defaults.icon;

  const finalTitle = title || defaults.title;
  const finalDescription = description || defaults.description;
  const finalActionLabel = actionLabel || defaults.actionLabel;
  const finalActionHref = actionHref || defaults.actionHref;

  return (
    <Card className={cn('border-dashed', className)}>
      <CardContent className="flex flex-col items-center justify-center py-16 px-6 text-center">
        {/* Icon */}
        <div className="mb-6 rounded-full bg-slate-100 dark:bg-slate-800 p-6">
          <Icon className="h-12 w-12 text-slate-400 dark:text-slate-500" />
        </div>

        {/* Title */}
        <h3 className="text-xl font-semibold text-slate-900 dark:text-slate-100 mb-3">
          {finalTitle}
        </h3>

        {/* Description */}
        <p className="text-slate-600 dark:text-slate-400 max-w-md mb-6">
          {finalDescription}
        </p>

        {/* Action Button */}
        {(finalActionHref || onAction) && (
          <>
            {finalActionHref ? (
              <Button asChild size="lg">
                <Link href={finalActionHref}>
                  <Upload className="mr-2 h-5 w-5" />
                  {finalActionLabel}
                </Link>
              </Button>
            ) : (
              <Button onClick={onAction} size="lg">
                {finalActionLabel}
              </Button>
            )}
          </>
        )}

        {/* Additional help text for first-time users */}
        {variant === 'no-documents' && (
          <div className="mt-8 text-sm text-slate-500 dark:text-slate-500">
            <p className="mb-2">Supported file types:</p>
            <p className="font-mono">PDF, DOCX, TXT, MD, and more</p>
          </div>
        )}
      </CardContent>
    </Card>
  );
}

/**
 * Empty State for Document Detail Page
 * Specialized variant for when a document is not found
 */
export function DocumentNotFoundState({
  documentId,
  className,
}: {
  documentId?: number;
  className?: string;
}) {
  return (
    <Card className={cn('border-dashed', className)}>
      <CardContent className="flex flex-col items-center justify-center py-16 px-6 text-center">
        <div className="mb-6 rounded-full bg-slate-100 dark:bg-slate-800 p-6">
          <FileText className="h-12 w-12 text-slate-400 dark:text-slate-500" />
        </div>

        <h3 className="text-xl font-semibold text-slate-900 dark:text-slate-100 mb-3">
          Document not found
        </h3>

        <p className="text-slate-600 dark:text-slate-400 max-w-md mb-6">
          {documentId
            ? `Document #${documentId} doesn't exist or you don't have permission to view it.`
            : 'The requested document could not be found.'}
        </p>

        <div className="flex gap-3">
          <Button variant="outline" asChild>
            <Link href="/documents">View All Documents</Link>
          </Button>
          <Button asChild>
            <Link href="/upload">
              <Upload className="mr-2 h-5 w-5" />
              Upload New Document
            </Link>
          </Button>
        </div>
      </CardContent>
    </Card>
  );
}

/**
 * Empty State for Processing Status
 * Shows when document is processing
 */
export function ProcessingState({
  message = 'Your document is being processed...',
  className,
}: {
  message?: string;
  className?: string;
}) {
  return (
    <Card className={cn('border-dashed', className)}>
      <CardContent className="flex flex-col items-center justify-center py-12 px-6 text-center">
        <div className="mb-6 rounded-full bg-blue-100 dark:bg-blue-900/30 p-6">
          <Upload className="h-12 w-12 text-blue-600 dark:text-blue-400 animate-pulse" />
        </div>

        <h3 className="text-lg font-semibold text-slate-900 dark:text-slate-100 mb-2">
          Processing Document
        </h3>

        <p className="text-slate-600 dark:text-slate-400 max-w-md">
          {message}
        </p>

        <p className="text-sm text-slate-500 dark:text-slate-500 mt-4">
          This may take a few moments. You can safely leave this page.
        </p>
      </CardContent>
    </Card>
  );
}
