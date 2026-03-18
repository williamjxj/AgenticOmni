/**
 * Text Preview Component
 * Shows extracted text preview from document
 * Feature: 005-view-embedded-docs / User Story 2
 */

import { useState, useEffect } from 'react';
import { FileText, Eye, EyeOff, ChevronDown, ChevronUp } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import { fetchDocumentTextPreview } from '@/lib/api/documents';
import { TextPreviewSkeleton } from '@/components/ui/skeleton';
import { getErrorMessage } from '@/lib/utils/error-handling';
import type { TextPreviewResponse } from '@/lib/types/document';

interface TextPreviewProps {
  documentId: number;
  maxPages?: number;
  previewLength?: number;
  defaultExpanded?: boolean;
}

/**
 * Text Preview Component
 * 
 * Displays:
 * - Extracted text preview from first N pages
 * - Page-by-page breakdown
 * - Extraction method indicators
 * - Confidence scores (for OCR)
 * - Expandable/collapsible view
 * 
 * @example
 * ```tsx
 * <TextPreview documentId={123} maxPages={5} />
 * ```
 */
export function TextPreview({
  documentId,
  maxPages = 5,
  previewLength = 1000,
  defaultExpanded = true,
}: TextPreviewProps) {
  const [preview, setPreview] = useState<TextPreviewResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isExpanded, setIsExpanded] = useState(defaultExpanded);
  const [showFullText, setShowFullText] = useState(false);

  useEffect(() => {
    async function loadPreview() {
      setLoading(true);
      setError(null);
      try {
        const data = await fetchDocumentTextPreview(documentId, maxPages, previewLength);
        setPreview(data);
      } catch (err) {
        setError(getErrorMessage(err));
      } finally {
        setLoading(false);
      }
    }

    if (documentId) {
      loadPreview();
    }
  }, [documentId, maxPages, previewLength]);

  if (loading) {
    return <TextPreviewSkeleton />;
  }

  if (error) {
    return (
      <Card>
        <CardContent className="p-6">
          <div className="flex items-start gap-3">
            <FileText className="h-5 w-5 text-red-600 flex-shrink-0 mt-0.5" />
            <div className="flex-1">
              <h3 className="text-lg font-semibold text-slate-900 dark:text-slate-100 mb-2">
                Text Preview Unavailable
              </h3>
              <p className="text-sm text-red-600 dark:text-red-400">
                {error}
              </p>
            </div>
          </div>
        </CardContent>
      </Card>
    );
  }

  if (!preview || !Array.isArray(preview.pages) || preview.pages.length === 0) {
    return (
      <Card>
        <CardContent className="p-6 text-center text-slate-600 dark:text-slate-400">
          <FileText className="h-8 w-8 mx-auto mb-2 opacity-50" />
          <p>No text content available for preview.</p>
        </CardContent>
      </Card>
    );
  }

  // Combine all page text for full preview
  const fullText = preview.pages.map(p => p.text_preview).join('\n\n');
  const truncatedText = fullText.length > previewLength 
    ? fullText.substring(0, previewLength) + '...'
    : fullText;

  return (
    <Card>
      <CardContent className="p-6 space-y-4">
        {/* Header */}
        <div className="flex items-start justify-between">
          <div className="flex items-center gap-3">
            <div className="p-2 rounded-lg bg-blue-100 dark:bg-blue-900/30">
              <FileText className="h-5 w-5 text-blue-600" />
            </div>
            <div>
              <h3 className="text-lg font-semibold text-slate-900 dark:text-slate-100">
                Text Preview
              </h3>
              <p className="text-sm text-slate-600 dark:text-slate-400">
                {preview.pages.length} {preview.pages.length === 1 ? 'page' : 'pages'} • {preview.total_characters.toLocaleString()} characters
              </p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <Button
              variant="ghost"
              size="sm"
              onClick={() => setShowFullText(!showFullText)}
              className="text-xs"
            >
              {showFullText ? (
                <>
                  <EyeOff className="h-3 w-3 mr-1" />
                  Truncate
                </>
              ) : (
                <>
                  <Eye className="h-3 w-3 mr-1" />
                  Show Full
                </>
              )}
            </Button>
            <Button
              variant="ghost"
              size="sm"
              onClick={() => setIsExpanded(!isExpanded)}
            >
              {isExpanded ? (
                <ChevronUp className="h-4 w-4" />
              ) : (
                <ChevronDown className="h-4 w-4" />
              )}
            </Button>
          </div>
        </div>

        {/* Content */}
        {isExpanded && (
          <div className="space-y-4">
            {/* Combined Text Preview */}
            <div className="bg-slate-50 dark:bg-slate-900 rounded-lg p-4 border border-slate-200 dark:border-slate-800">
              <pre className="text-sm text-slate-700 dark:text-slate-300 whitespace-pre-wrap font-sans leading-relaxed">
                {showFullText ? fullText : truncatedText}
              </pre>
              {!showFullText && fullText.length > previewLength && (
                <Button
                  variant="link"
                  size="sm"
                  onClick={() => setShowFullText(true)}
                  className="mt-2 px-0"
                >
                  Show more...
                </Button>
              )}
            </div>

            {/* Page-by-Page Breakdown */}
            {preview.pages.length > 1 && (
              <div className="pt-3 border-t border-slate-200 dark:border-slate-800">
                <h4 className="text-sm font-semibold text-slate-900 dark:text-slate-100 mb-3">
                  Page Breakdown
                </h4>
                <div className="space-y-2">
                  {preview.pages.map((page) => (
                    <details
                      key={page.page_number}
                      className="group border border-slate-200 dark:border-slate-800 rounded-lg overflow-hidden"
                    >
                      <summary className="px-4 py-2 cursor-pointer hover:bg-slate-50 dark:hover:bg-slate-900 flex items-center justify-between">
                        <div className="flex items-center gap-3">
                          <span className="text-sm font-medium text-slate-900 dark:text-slate-100">
                            Page {page.page_number}
                          </span>
                          <span className="text-xs px-2 py-0.5 rounded-full bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-400">
                            {page.extraction_method}
                          </span>
                          {page.confidence_score !== undefined && (
                            <span className="text-xs text-slate-600 dark:text-slate-400">
                              {(page.confidence_score * 100).toFixed(0)}% confidence
                            </span>
                          )}
                        </div>
                        <ChevronDown className="h-4 w-4 text-slate-400 group-open:rotate-180 transition-transform" />
                      </summary>
                      <div className="px-4 py-3 bg-slate-50 dark:bg-slate-900 border-t border-slate-200 dark:border-slate-800">
                        <pre className="text-xs text-slate-700 dark:text-slate-300 whitespace-pre-wrap font-sans">
                          {page.text_preview}
                        </pre>
                      </div>
                    </details>
                  ))}
                </div>
              </div>
            )}

            {/* Extraction Methods Summary */}
            <div className="pt-3 border-t border-slate-200 dark:border-slate-800">
              <h4 className="text-sm font-semibold text-slate-900 dark:text-slate-100 mb-2">
                Extraction Methods
              </h4>
              <div className="flex flex-wrap gap-2">
                {Array.from(new Set(preview.pages.map(p => p.extraction_method))).map((method) => {
                  const count = preview.pages.filter(p => p.extraction_method === method).length;
                  return (
                    <div
                      key={method}
                      className="px-3 py-1 rounded-full bg-slate-100 dark:bg-slate-800 text-xs"
                    >
                      <span className="font-medium text-slate-900 dark:text-slate-100">
                        {method}
                      </span>
                      <span className="text-slate-600 dark:text-slate-400 ml-1">
                        ({count} {count === 1 ? 'page' : 'pages'})
                      </span>
                    </div>
                  );
                })}
              </div>
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
}

/**
 * Compact Text Preview
 * Simplified version for smaller spaces
 */
export function CompactTextPreview({
  documentId,
  previewLength = 300,
}: Pick<TextPreviewProps, 'documentId' | 'previewLength'>) {
  const [preview, setPreview] = useState<TextPreviewResponse | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadPreview() {
      try {
        const data = await fetchDocumentTextPreview(documentId, 1, previewLength);
        setPreview(data);
      } catch (err) {
        // Silently fail for compact preview
      } finally {
        setLoading(false);
      }
    }

    if (documentId) {
      loadPreview();
    }
  }, [documentId, previewLength]);

  if (loading || !preview || preview.pages.length === 0) {
    return null;
  }

  const firstPageText = preview.pages[0].text_preview;

  return (
    <div className="bg-slate-50 dark:bg-slate-900 rounded-lg p-3 border border-slate-200 dark:border-slate-800">
      <p className="text-xs text-slate-700 dark:text-slate-300 line-clamp-3">
        {firstPageText}
      </p>
    </div>
  );
}
