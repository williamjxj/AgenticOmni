/**
 * Chunk Item Component
 * Displays individual chunk with expandable details
 * Feature: 005-view-embedded-docs / User Story 4
 */

import { ChevronDown, ChevronUp, FileText, Hash, MapPin, CheckCircle2, XCircle } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { cn } from '@/lib/utils';
import { formatDate } from '@/lib/utils/date';
import { formatTokenCount } from '@/lib/utils/format';
import type { DocumentChunk } from '@/lib/types/document';

interface ChunkItemProps {
  chunk: DocumentChunk;
  isExpanded?: boolean;
  onToggleExpand?: () => void;
  showFullContent?: boolean;
  className?: string;
}

/**
 * Get chunk type badge config
 */
function getChunkTypeBadge(type?: string) {
  const badges = {
    text: { label: 'Text', color: 'bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-200' },
    table: { label: 'Table', color: 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-200' },
    list: { label: 'List', color: 'bg-purple-100 text-purple-800 dark:bg-purple-900/30 dark:text-purple-200' },
    heading: { label: 'Heading', color: 'bg-amber-100 text-amber-800 dark:bg-amber-900/30 dark:text-amber-200' },
    code: { label: 'Code', color: 'bg-slate-100 text-slate-800 dark:bg-slate-800 dark:text-slate-200' },
  };
  return badges[type as keyof typeof badges] || badges.text;
}

/**
 * Chunk Item Component
 * 
 * Displays:
 * - Chunk sequence number
 * - Content preview/full text
 * - Token count
 * - Page range
 * - Chunk type
 * - Embedding status
 * - Metadata (section headings, offsets)
 * - Expandable details
 * 
 * @example
 * ```tsx
 * <ChunkItem
 *   chunk={chunk}
 *   isExpanded={expanded}
 *   onToggleExpand={() => setExpanded(!expanded)}
 * />
 * ```
 */
export function ChunkItem({
  chunk,
  isExpanded = false,
  onToggleExpand,
  showFullContent = false,
  className,
}: ChunkItemProps) {
  const hasEmbedding = chunk.embedding_vector !== null;
  const chunkTypeBadge = getChunkTypeBadge(chunk.chunk_type);
  const previewLength = 200;
  const needsTruncation = chunk.content_text.length > previewLength;
  const displayText = !isExpanded && needsTruncation && !showFullContent
    ? chunk.content_text.substring(0, previewLength) + '...'
    : chunk.content_text;

  return (
    <div
      className={cn(
        'border rounded-lg overflow-hidden transition-all',
        hasEmbedding
          ? 'border-slate-200 dark:border-slate-800'
          : 'border-amber-200 dark:border-amber-800 bg-amber-50/50 dark:bg-amber-950/20',
        className
      )}
    >
      {/* Header */}
      <div className="px-4 py-3 bg-slate-50 dark:bg-slate-900 border-b border-slate-200 dark:border-slate-800">
        <div className="flex items-start justify-between gap-3">
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-2 mb-1">
              {/* Chunk Number */}
              <span className="text-sm font-semibold text-slate-900 dark:text-slate-100 flex items-center gap-1">
                <Hash className="h-3 w-3" />
                Chunk {chunk.chunk_sequence}
              </span>

              {/* Chunk Type Badge */}
              <span className={cn('text-xs px-2 py-0.5 rounded-full', chunkTypeBadge.color)}>
                {chunkTypeBadge.label}
              </span>

              {/* Embedding Status */}
              {hasEmbedding ? (
                <span className="text-xs flex items-center gap-1 text-green-600 dark:text-green-400">
                  <CheckCircle2 className="h-3 w-3" />
                  Embedded
                </span>
              ) : (
                <span className="text-xs flex items-center gap-1 text-amber-600 dark:text-amber-400">
                  <XCircle className="h-3 w-3" />
                  No Embedding
                </span>
              )}
            </div>

            {/* Metadata Row */}
            <div className="flex flex-wrap items-center gap-3 text-xs text-slate-600 dark:text-slate-400">
              {/* Token Count */}
              {chunk.token_count && (
                <span className="flex items-center gap-1">
                  <FileText className="h-3 w-3" />
                  {formatTokenCount(chunk.token_count)} tokens
                </span>
              )}

              {/* Page Range */}
              {chunk.start_page && (
                <span className="flex items-center gap-1">
                  <MapPin className="h-3 w-3" />
                  Page {chunk.start_page}
                  {chunk.end_page && chunk.end_page !== chunk.start_page && (
                    <>-{chunk.end_page}</>
                  )}
                </span>
              )}

              {/* Character Offsets */}
              {chunk.char_offset_start !== null && chunk.char_offset_end !== null && (
                <span>
                  Chars {chunk.char_offset_start}-{chunk.char_offset_end}
                </span>
              )}
            </div>

            {/* Section Heading */}
            {chunk.section_heading && (
              <div className="mt-2 text-xs">
                <span className="text-slate-600 dark:text-slate-400">Section: </span>
                <span className="font-medium text-slate-900 dark:text-slate-100">
                  {chunk.section_heading}
                </span>
              </div>
            )}
          </div>

          {/* Expand/Collapse Button */}
          {onToggleExpand && needsTruncation && !showFullContent && (
            <Button
              variant="ghost"
              size="sm"
              onClick={onToggleExpand}
              className="flex-shrink-0"
            >
              {isExpanded ? (
                <ChevronUp className="h-4 w-4" />
              ) : (
                <ChevronDown className="h-4 w-4" />
              )}
            </Button>
          )}
        </div>
      </div>

      {/* Content */}
      <div className="px-4 py-3">
        <pre className="text-sm text-slate-700 dark:text-slate-300 whitespace-pre-wrap font-sans leading-relaxed">
          {displayText}
        </pre>
      </div>

      {/* Expanded Details */}
      {isExpanded && (
        <div className="px-4 py-3 border-t border-slate-200 dark:border-slate-800 bg-slate-50 dark:bg-slate-900">
          <h5 className="text-xs font-semibold text-slate-900 dark:text-slate-100 mb-2">
            Technical Details
          </h5>
          <dl className="grid grid-cols-2 gap-3 text-xs">
            <div>
              <dt className="text-slate-600 dark:text-slate-400">Chunk ID</dt>
              <dd className="font-mono text-slate-900 dark:text-slate-100 mt-0.5">
                {chunk.chunk_id}
              </dd>
            </div>
            <div>
              <dt className="text-slate-600 dark:text-slate-400">Order</dt>
              <dd className="font-mono text-slate-900 dark:text-slate-100 mt-0.5">
                {chunk.chunk_order}
              </dd>
            </div>
            {chunk.embedding_model && (
              <div className="col-span-2">
                <dt className="text-slate-600 dark:text-slate-400">Embedding Model</dt>
                <dd className="font-mono text-slate-900 dark:text-slate-100 mt-0.5">
                  {chunk.embedding_model}
                </dd>
              </div>
            )}
            {chunk.embedding_generated_at && (
              <div className="col-span-2">
                <dt className="text-slate-600 dark:text-slate-400">Embedded At</dt>
                <dd className="text-slate-900 dark:text-slate-100 mt-0.5">
                  {formatDate(chunk.embedding_generated_at)}
                </dd>
              </div>
            )}
            {chunk.parent_heading && (
              <div className="col-span-2">
                <dt className="text-slate-600 dark:text-slate-400">Parent Heading</dt>
                <dd className="text-slate-900 dark:text-slate-100 mt-0.5">
                  {chunk.parent_heading}
                </dd>
              </div>
            )}
            <div className="col-span-2">
              <dt className="text-slate-600 dark:text-slate-400">Created At</dt>
              <dd className="text-slate-900 dark:text-slate-100 mt-0.5">
                {formatDate(chunk.created_at)}
              </dd>
            </div>
          </dl>
        </div>
      )}
    </div>
  );
}

/**
 * Compact Chunk Item
 * Minimal display for lists or cards
 */
export function CompactChunkItem({ chunk }: { chunk: DocumentChunk }) {
  const hasEmbedding = chunk.embedding_vector !== null;

  return (
    <div className="flex items-start gap-3 p-2 hover:bg-slate-50 dark:hover:bg-slate-900 rounded-lg transition-colors">
      <div className="flex-shrink-0 w-12 text-center">
        <span className="text-xs font-semibold text-slate-600 dark:text-slate-400">
          #{chunk.chunk_sequence}
        </span>
      </div>
      <div className="flex-1 min-w-0">
        <p className="text-sm text-slate-700 dark:text-slate-300 line-clamp-2">
          {chunk.content_text}
        </p>
        <div className="flex items-center gap-2 mt-1 text-xs text-slate-600 dark:text-slate-400">
          {chunk.token_count && <span>{formatTokenCount(chunk.token_count)} tokens</span>}
          {hasEmbedding ? (
            <span className="text-green-600 dark:text-green-400">✓ Embedded</span>
          ) : (
            <span className="text-amber-600 dark:text-amber-400">No embedding</span>
          )}
        </div>
      </div>
    </div>
  );
}
