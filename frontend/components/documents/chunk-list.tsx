/**
 * Chunk List Component
 * Displays a paginated list of document chunks
 * Feature: 005-view-embedded-docs / User Story 4
 */

import { useState, useEffect } from 'react';
import { Layers, ChevronLeft, ChevronRight } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { ChunkItem } from './chunk-item';
import { ChunkListSkeleton } from '@/components/ui/skeleton';
import { fetchDocumentChunks } from '@/lib/api/documents';
import { getErrorMessage } from '@/lib/utils/error-handling';
import type { DocumentChunk } from '@/lib/types/document';

interface ChunkListProps {
  documentId: number;
  pageSize?: number;
  showPagination?: boolean;
  className?: string;
}

/**
 * Chunk List Component
 * 
 * Displays:
 * - Paginated list of chunks
 * - Chunk sequence numbers
 * - Chunk content preview
 * - Token counts
 * - Page ranges
 * - Embedding status
 * - Pagination controls
 * 
 * @example
 * ```tsx
 * <ChunkList documentId={123} pageSize={10} />
 * ```
 */
export function ChunkList({
  documentId,
  pageSize = 10,
  showPagination = true,
  className,
}: ChunkListProps) {
  const [chunks, setChunks] = useState<DocumentChunk[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [page, setPage] = useState(1);
  const [totalChunks, setTotalChunks] = useState(0);
  const [expandedChunkId, setExpandedChunkId] = useState<number | null>(null);

  const totalPages = Math.ceil(totalChunks / pageSize);

  useEffect(() => {
    async function loadChunks() {
      setLoading(true);
      setError(null);
      try {
        const response = await fetchDocumentChunks(documentId, page, pageSize);
        setChunks(response.chunks);
        setTotalChunks(response.total);
      } catch (err) {
        setError(getErrorMessage(err));
      } finally {
        setLoading(false);
      }
    }

    loadChunks();
  }, [documentId, page, pageSize]);

  const handleToggleExpand = (chunkId: number) => {
    setExpandedChunkId(expandedChunkId === chunkId ? null : chunkId);
  };

  if (loading) {
    return <ChunkListSkeleton count={3} />;
  }

  if (error) {
    return (
      <div className="bg-red-50 dark:bg-red-950/30 border border-red-200 dark:border-red-800 rounded-lg p-4">
        <p className="text-sm text-red-700 dark:text-red-300">{error}</p>
      </div>
    );
  }

  if (chunks.length === 0) {
    return (
      <div className="text-center py-8 text-slate-600 dark:text-slate-400">
        <Layers className="h-8 w-8 mx-auto mb-2 opacity-50" />
        <p className="text-sm">No chunks available for this document.</p>
      </div>
    );
  }

  return (
    <div className={className}>
      <div className="space-y-3">
        {chunks.map((chunk) => (
          <ChunkItem
            key={chunk.chunk_id}
            chunk={chunk}
            isExpanded={expandedChunkId === chunk.chunk_id}
            onToggleExpand={() => handleToggleExpand(chunk.chunk_id)}
          />
        ))}
      </div>

      {/* Pagination */}
      {showPagination && totalPages > 1 && (
        <div className="flex items-center justify-between mt-4 pt-4 border-t border-slate-200 dark:border-slate-800">
          <div className="text-sm text-slate-600 dark:text-slate-400">
            Showing {(page - 1) * pageSize + 1}-{Math.min(page * pageSize, totalChunks)} of{' '}
            {totalChunks} chunks
          </div>
          <div className="flex items-center gap-2">
            <Button
              variant="outline"
              size="sm"
              onClick={() => setPage((p) => Math.max(1, p - 1))}
              disabled={page === 1}
            >
              <ChevronLeft className="h-4 w-4" />
            </Button>
            <span className="text-sm text-slate-600 dark:text-slate-400 min-w-[80px] text-center">
              Page {page} of {totalPages}
            </span>
            <Button
              variant="outline"
              size="sm"
              onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
              disabled={page === totalPages}
            >
              <ChevronRight className="h-4 w-4" />
            </Button>
          </div>
        </div>
      )}
    </div>
  );
}

/**
 * Compact Chunk List
 * Simplified list without pagination for smaller spaces
 */
export function CompactChunkList({
  chunks,
  maxChunks = 5,
}: {
  chunks: DocumentChunk[];
  maxChunks?: number;
}) {
  const displayChunks = chunks.slice(0, maxChunks);
  const hasMore = chunks.length > maxChunks;

  return (
    <div className="space-y-2">
      {displayChunks.map((chunk) => (
        <div
          key={chunk.chunk_id}
          className="border border-slate-200 dark:border-slate-800 rounded-lg p-3"
        >
          <div className="flex items-center justify-between mb-2">
            <span className="text-xs font-semibold text-slate-900 dark:text-slate-100">
              Chunk #{chunk.chunk_sequence}
            </span>
            {chunk.token_count && (
              <span className="text-xs text-slate-600 dark:text-slate-400">
                {chunk.token_count} tokens
              </span>
            )}
          </div>
          <p className="text-xs text-slate-700 dark:text-slate-300 line-clamp-2">
            {chunk.content_text}
          </p>
        </div>
      ))}
      {hasMore && (
        <p className="text-xs text-center text-slate-600 dark:text-slate-400">
          +{chunks.length - maxChunks} more chunks
        </p>
      )}
    </div>
  );
}

/**
 * Chunk List Summary
 * Shows quick statistics about chunks
 */
export function ChunkListSummary({ chunks }: { chunks: DocumentChunk[] }) {
  const withEmbeddings = chunks.filter((c) => c.embedding_vector !== null).length;
  const avgTokens =
    chunks.reduce((sum, c) => sum + (c.token_count || 0), 0) / chunks.length;

  return (
    <div className="flex flex-wrap items-center gap-4 text-sm">
      <div>
        <span className="text-slate-600 dark:text-slate-400">Total: </span>
        <span className="font-semibold text-slate-900 dark:text-slate-100">
          {chunks.length}
        </span>
      </div>
      <div>
        <span className="text-slate-600 dark:text-slate-400">Embedded: </span>
        <span className="font-semibold text-slate-900 dark:text-slate-100">
          {withEmbeddings}
        </span>
      </div>
      <div>
        <span className="text-slate-600 dark:text-slate-400">Avg Tokens: </span>
        <span className="font-semibold text-slate-900 dark:text-slate-100">
          {avgTokens.toFixed(0)}
        </span>
      </div>
    </div>
  );
}
