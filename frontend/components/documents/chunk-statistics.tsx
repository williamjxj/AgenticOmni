/**
 * Chunk Statistics Component
 * Displays statistical information about document chunks
 * Feature: 005-view-embedded-docs / User Story 4
 */

import { TrendingUp, BarChart3, FileText } from 'lucide-react';
import { formatNumber, formatTokenCount } from '@/lib/utils/format';
import type { EmbeddingStatistics } from '@/lib/types/document';

interface ChunkStatisticsProps {
  statistics: EmbeddingStatistics;
}

/**
 * Chunk Statistics Component
 * 
 * Displays:
 * - Total chunks
 * - Chunks with embeddings
 * - Embedding coverage percentage
 * - Average, min, and max chunk sizes
 * - Visual progress bar
 * 
 * @example
 * ```tsx
 * <ChunkStatistics statistics={embeddingStats} />
 * ```
 */
export function ChunkStatistics({ statistics }: ChunkStatisticsProps) {
  const coveragePercent = statistics.embedding_coverage || 0;
  const isFullyCovered = coveragePercent >= 100;

  return (
    <div className="space-y-4">
      {/* Coverage Progress Bar */}
      <div>
        <div className="flex items-center justify-between text-sm mb-2">
          <span className="text-slate-600 dark:text-slate-400">Embedding Coverage</span>
          <span className="font-semibold text-slate-900 dark:text-slate-100">
            {coveragePercent.toFixed(1)}%
          </span>
        </div>
        <div className="h-3 bg-slate-200 dark:bg-slate-800 rounded-full overflow-hidden">
          <div
            className={`h-full transition-all duration-500 ${
              isFullyCovered
                ? 'bg-green-600 dark:bg-green-400'
                : 'bg-purple-600 dark:bg-purple-400'
            }`}
            style={{ width: `${Math.min(coveragePercent, 100)}%` }}
          />
        </div>
        {!isFullyCovered && (
          <p className="text-xs text-amber-600 dark:text-amber-400 mt-1">
            {statistics.total_chunks - statistics.chunks_with_embeddings} chunks pending
          </p>
        )}
      </div>

      {/* Statistics Grid */}
      <div className="grid grid-cols-2 sm:grid-cols-3 gap-4">
        {/* Total Chunks */}
        <div className="bg-slate-50 dark:bg-slate-900 rounded-lg p-3">
          <div className="flex items-center gap-2 mb-1">
            <FileText className="h-4 w-4 text-blue-600" />
            <dt className="text-xs text-slate-600 dark:text-slate-400">Total Chunks</dt>
          </div>
          <dd className="text-xl font-bold text-slate-900 dark:text-slate-100">
            {formatNumber(statistics.total_chunks)}
          </dd>
        </div>

        {/* With Embeddings */}
        <div className="bg-slate-50 dark:bg-slate-900 rounded-lg p-3">
          <div className="flex items-center gap-2 mb-1">
            <TrendingUp className="h-4 w-4 text-green-600" />
            <dt className="text-xs text-slate-600 dark:text-slate-400">Embedded</dt>
          </div>
          <dd className="text-xl font-bold text-slate-900 dark:text-slate-100">
            {formatNumber(statistics.chunks_with_embeddings)}
          </dd>
        </div>

        {/* Average Size */}
        <div className="bg-slate-50 dark:bg-slate-900 rounded-lg p-3">
          <div className="flex items-center gap-2 mb-1">
            <BarChart3 className="h-4 w-4 text-purple-600" />
            <dt className="text-xs text-slate-600 dark:text-slate-400">Avg. Size</dt>
          </div>
          <dd className="text-xl font-bold text-slate-900 dark:text-slate-100">
            {formatTokenCount(statistics.avg_chunk_size)}
          </dd>
          <dd className="text-xs text-slate-600 dark:text-slate-400 mt-0.5">tokens</dd>
        </div>

        {/* Min Size */}
        <div className="bg-slate-50 dark:bg-slate-900 rounded-lg p-3">
          <dt className="text-xs text-slate-600 dark:text-slate-400 mb-1">Min Size</dt>
          <dd className="text-lg font-semibold text-slate-900 dark:text-slate-100">
            {formatTokenCount(statistics.min_chunk_size)}
          </dd>
          <dd className="text-xs text-slate-600 dark:text-slate-400">tokens</dd>
        </div>

        {/* Max Size */}
        <div className="bg-slate-50 dark:bg-slate-900 rounded-lg p-3">
          <dt className="text-xs text-slate-600 dark:text-slate-400 mb-1">Max Size</dt>
          <dd className="text-lg font-semibold text-slate-900 dark:text-slate-100">
            {formatTokenCount(statistics.max_chunk_size)}
          </dd>
          <dd className="text-xs text-slate-600 dark:text-slate-400">tokens</dd>
        </div>

        {/* Size Range */}
        <div className="bg-slate-50 dark:bg-slate-900 rounded-lg p-3">
          <dt className="text-xs text-slate-600 dark:text-slate-400 mb-1">Size Range</dt>
          <dd className="text-lg font-semibold text-slate-900 dark:text-slate-100">
            {formatTokenCount(statistics.max_chunk_size - statistics.min_chunk_size)}
          </dd>
          <dd className="text-xs text-slate-600 dark:text-slate-400">spread</dd>
        </div>
      </div>

      {/* Additional Info */}
      <div className="bg-blue-50 dark:bg-blue-950/30 border border-blue-200 dark:border-blue-800 rounded-lg p-3">
        <p className="text-xs text-blue-900 dark:text-blue-100">
          <strong>How it works:</strong> Documents are split into overlapping chunks for better context preservation. Each chunk is converted into a {statistics.vector_dimensions}-dimensional vector using the {statistics.embedding_model} model.
        </p>
      </div>
    </div>
  );
}

/**
 * Compact Chunk Statistics
 * Minimal statistics display for cards or sidebars
 */
export function CompactChunkStatistics({ statistics }: ChunkStatisticsProps) {
  return (
    <div className="flex items-center gap-4 text-sm">
      <div>
        <span className="text-slate-600 dark:text-slate-400">Chunks: </span>
        <span className="font-semibold text-slate-900 dark:text-slate-100">
          {statistics.total_chunks}
        </span>
      </div>
      <div>
        <span className="text-slate-600 dark:text-slate-400">Avg: </span>
        <span className="font-semibold text-slate-900 dark:text-slate-100">
          {formatTokenCount(statistics.avg_chunk_size)}
        </span>
      </div>
      <div>
        <span className="text-slate-600 dark:text-slate-400">Coverage: </span>
        <span className="font-semibold text-slate-900 dark:text-slate-100">
          {statistics.embedding_coverage.toFixed(0)}%
        </span>
      </div>
    </div>
  );
}

/**
 * Chunk Size Distribution Visualization
 * Simple bar chart showing chunk size distribution
 */
export function ChunkSizeDistribution({ statistics }: ChunkStatisticsProps) {
  const { min_chunk_size, avg_chunk_size, max_chunk_size } = statistics;
  
  // Calculate percentages for visual representation
  const range = max_chunk_size - min_chunk_size;
  const avgPosition = range > 0 ? ((avg_chunk_size - min_chunk_size) / range) * 100 : 50;

  return (
    <div className="space-y-2">
      <h5 className="text-xs font-semibold text-slate-900 dark:text-slate-100">
        Chunk Size Distribution
      </h5>
      <div className="relative h-8 bg-slate-200 dark:bg-slate-800 rounded-lg overflow-hidden">
        {/* Min marker */}
        <div className="absolute left-0 top-0 bottom-0 w-1 bg-blue-600" />
        
        {/* Average marker */}
        <div
          className="absolute top-0 bottom-0 w-1 bg-green-600"
          style={{ left: `${avgPosition}%` }}
        />
        
        {/* Max marker */}
        <div className="absolute right-0 top-0 bottom-0 w-1 bg-red-600" />

        {/* Gradient fill */}
        <div className="absolute inset-0 bg-gradient-to-r from-blue-500/20 via-green-500/20 to-red-500/20" />
      </div>
      
      {/* Legend */}
      <div className="flex items-center justify-between text-xs">
        <div className="flex items-center gap-1">
          <div className="w-2 h-2 rounded-full bg-blue-600" />
          <span className="text-slate-600 dark:text-slate-400">
            Min: {formatTokenCount(min_chunk_size)}
          </span>
        </div>
        <div className="flex items-center gap-1">
          <div className="w-2 h-2 rounded-full bg-green-600" />
          <span className="text-slate-600 dark:text-slate-400">
            Avg: {formatTokenCount(avg_chunk_size)}
          </span>
        </div>
        <div className="flex items-center gap-1">
          <div className="w-2 h-2 rounded-full bg-red-600" />
          <span className="text-slate-600 dark:text-slate-400">
            Max: {formatTokenCount(max_chunk_size)}
          </span>
        </div>
      </div>
    </div>
  );
}
