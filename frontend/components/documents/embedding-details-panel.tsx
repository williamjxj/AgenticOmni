/**
 * Embedding Details Panel Component
 * Displays comprehensive embedding information with expandable sections
 * Feature: 005-view-embedded-docs / User Story 4
 */

import { useState, useEffect } from 'react';
import { ChevronDown, ChevronUp, Sparkles, Info, Database, Layers } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import { cn } from '@/lib/utils';
import { ChunkStatistics } from './chunk-statistics';
import { ChunkList } from './chunk-list';
import { fetchEmbeddingStatistics } from '@/lib/api/documents';
import { getErrorMessage } from '@/lib/utils/error-handling';
import { formatModelName, formatVectorDimensions } from '@/lib/utils/format';
import type { Document, EmbeddingStatistics } from '@/lib/types/document';

interface EmbeddingDetailsPanelProps {
  document: Document;
  defaultExpanded?: boolean;
  className?: string;
}

/**
 * Tooltip Component for Technical Terms
 */
function InfoTooltip({ text }: { text: string }) {
  return (
    <div className="group relative inline-flex">
      <Info className="h-4 w-4 text-slate-400 hover:text-slate-600 dark:hover:text-slate-300 cursor-help" />
      <div className="absolute bottom-full left-1/2 -translate-x-1/2 mb-2 px-3 py-2 bg-slate-900 dark:bg-slate-100 text-white dark:text-slate-900 text-xs rounded-lg opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all duration-200 whitespace-nowrap z-10 pointer-events-none max-w-xs text-left">
        {text}
        <div className="absolute top-full left-1/2 -translate-x-1/2 -mt-1 border-4 border-transparent border-t-slate-900 dark:border-t-slate-100" />
      </div>
    </div>
  );
}

/**
 * Embedding Details Panel Component
 * 
 * Displays:
 * - Embedding model information
 * - Vector dimensions
 * - Chunk statistics
 * - Chunk list with details
 * - Expandable/collapsible sections
 * 
 * @example
 * ```tsx
 * <EmbeddingDetailsPanel document={document} defaultExpanded={false} />
 * ```
 */
export function EmbeddingDetailsPanel({
  document,
  defaultExpanded = false,
  className,
}: EmbeddingDetailsPanelProps) {
  const [isExpanded, setIsExpanded] = useState(defaultExpanded);
  const [showChunks, setShowChunks] = useState(false);
  const [statistics, setStatistics] = useState<EmbeddingStatistics | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const hasEmbeddings = document.embedding_status === 'completed';
  const chunkCount = document.chunks?.length || document.chunk_count || 0;

  // Fetch embedding statistics when expanded
  useEffect(() => {
    async function loadStatistics() {
      if (!isExpanded || !hasEmbeddings || statistics) return;

      setLoading(true);
      setError(null);
      try {
        const stats = await fetchEmbeddingStatistics(document.document_id);
        setStatistics(stats);
      } catch (err) {
        setError(getErrorMessage(err));
      } finally {
        setLoading(false);
      }
    }

    loadStatistics();
  }, [isExpanded, hasEmbeddings, document.document_id, statistics]);

  // Not available state
  if (!hasEmbeddings) {
    return (
      <Card className={cn('border-dashed', className)}>
        <CardContent className="p-6">
          <div className="flex items-start gap-3">
            <div className="p-2 rounded-lg bg-slate-100 dark:bg-slate-800">
              <Sparkles className="h-5 w-5 text-slate-400" />
            </div>
            <div className="flex-1">
              <h3 className="text-lg font-semibold text-slate-900 dark:text-slate-100 mb-2">
                Embedding Details
              </h3>
              <p className="text-sm text-slate-600 dark:text-slate-400">
                Embeddings have not been generated for this document yet.
                {document.processing_status === 'parsed' && (
                  <> Generate embeddings to view technical details and enable semantic search.</>
                )}
              </p>
            </div>
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className={className}>
      <CardContent className="p-6 space-y-4">
        {/* Header */}
        <div className="flex items-start justify-between">
          <div className="flex items-center gap-3">
            <div className="p-2 rounded-lg bg-purple-100 dark:bg-purple-900/30">
              <Sparkles className="h-5 w-5 text-purple-600" />
            </div>
            <div>
              <h3 className="text-lg font-semibold text-slate-900 dark:text-slate-100 flex items-center gap-2">
                Embedding Details
                <InfoTooltip text="Technical information about vector embeddings used for semantic search" />
              </h3>
              <p className="text-sm text-slate-600 dark:text-slate-400">
                Vector embeddings and chunk information
              </p>
            </div>
          </div>
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

        {/* Quick Stats (Always Visible) */}
        {!isExpanded && (
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 pt-2">
            <div>
              <dt className="text-xs text-slate-600 dark:text-slate-400 mb-1">Model</dt>
              <dd className="text-sm font-medium text-slate-900 dark:text-slate-100 truncate">
                {statistics?.embedding_model || 'Loading...'}
              </dd>
            </div>
            <div>
              <dt className="text-xs text-slate-600 dark:text-slate-400 mb-1">Dimensions</dt>
              <dd className="text-sm font-medium text-slate-900 dark:text-slate-100">
                {statistics?.vector_dimensions || '—'}
              </dd>
            </div>
            <div>
              <dt className="text-xs text-slate-600 dark:text-slate-400 mb-1">Chunks</dt>
              <dd className="text-sm font-medium text-slate-900 dark:text-slate-100">
                {chunkCount}
              </dd>
            </div>
            <div>
              <dt className="text-xs text-slate-600 dark:text-slate-400 mb-1">Coverage</dt>
              <dd className="text-sm font-medium text-slate-900 dark:text-slate-100">
                {statistics?.embedding_coverage?.toFixed(0) || '—'}%
              </dd>
            </div>
          </div>
        )}

        {/* Expanded Content */}
        {isExpanded && (
          <div className="space-y-6 pt-2">
            {loading && (
              <div className="text-center py-8">
                <div className="animate-spin h-8 w-8 border-4 border-purple-600 border-t-transparent rounded-full mx-auto mb-2" />
                <p className="text-sm text-slate-600 dark:text-slate-400">Loading embedding details...</p>
              </div>
            )}

            {error && (
              <div className="bg-red-50 dark:bg-red-950/30 border border-red-200 dark:border-red-800 rounded-lg p-4">
                <p className="text-sm text-red-700 dark:text-red-300">{error}</p>
              </div>
            )}

            {!loading && !error && statistics && (
              <>
                {/* Model Information */}
                <div className="border-t border-slate-200 dark:border-slate-800 pt-4">
                  <h4 className="text-sm font-semibold text-slate-900 dark:text-slate-100 mb-3 flex items-center gap-2">
                    <Database className="h-4 w-4" />
                    Model Information
                  </h4>
                  <dl className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                    <div>
                      <dt className="text-sm text-slate-600 dark:text-slate-400 mb-1 flex items-center gap-1">
                        Model Name
                        <InfoTooltip text="The AI model used to generate vector embeddings" />
                      </dt>
                      <dd className="text-sm font-medium text-slate-900 dark:text-slate-100">
                        {formatModelName(statistics.embedding_model)}
                      </dd>
                    </div>
                    <div>
                      <dt className="text-sm text-slate-600 dark:text-slate-400 mb-1 flex items-center gap-1">
                        Vector Dimensions
                        <InfoTooltip text="The size of each embedding vector. Higher dimensions can capture more semantic nuance but require more storage." />
                      </dt>
                      <dd className="text-sm font-medium text-slate-900 dark:text-slate-100">
                        {formatVectorDimensions(statistics.vector_dimensions)}
                      </dd>
                    </div>
                  </dl>
                </div>

                {/* Chunk Statistics */}
                <div className="border-t border-slate-200 dark:border-slate-800 pt-4">
                  <h4 className="text-sm font-semibold text-slate-900 dark:text-slate-100 mb-3 flex items-center gap-2">
                    <Layers className="h-4 w-4" />
                    Chunk Statistics
                    <InfoTooltip text="Documents are split into chunks for efficient embedding and retrieval" />
                  </h4>
                  <ChunkStatistics statistics={statistics} />
                </div>

                {/* Chunk List Toggle */}
                <div className="border-t border-slate-200 dark:border-slate-800 pt-4">
                  <div className="flex items-center justify-between mb-3">
                    <h4 className="text-sm font-semibold text-slate-900 dark:text-slate-100 flex items-center gap-2">
                      <Layers className="h-4 w-4" />
                      Document Chunks ({chunkCount})
                    </h4>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => setShowChunks(!showChunks)}
                    >
                      {showChunks ? 'Hide' : 'Show'} Chunks
                    </Button>
                  </div>

                  {showChunks && (
                    <ChunkList documentId={document.document_id} />
                  )}
                </div>
              </>
            )}
          </div>
        )}
      </CardContent>
    </Card>
  );
}

/**
 * Compact Embedding Summary
 * Minimal display for sidebars or cards
 */
export function CompactEmbeddingSummary({ document }: { document: Document }) {
  const hasEmbeddings = document.embedding_status === 'completed';
  const chunkCount = document.chunks?.length || 0;

  if (!hasEmbeddings) return null;

  return (
    <div className="flex items-center gap-4 text-xs text-slate-600 dark:text-slate-400">
      <div className="flex items-center gap-1">
        <Sparkles className="h-3 w-3" />
        <span>{chunkCount} chunks</span>
      </div>
      <div className="flex items-center gap-1">
        <Database className="h-3 w-3" />
        <span>Embedded</span>
      </div>
    </div>
  );
}
