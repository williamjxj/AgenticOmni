/**
 * Embedding Status Card Component
 * Shows embedding generation status and statistics
 * Feature: 005-view-embedded-docs / User Story 2
 */

import { Sparkles, CheckCircle2, XCircle, Clock, RefreshCw, TrendingUp } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import { StatusBadge } from './status-badge';
import { formatRelativeTime, getDuration } from '@/lib/utils/date';
import type { Document } from '@/lib/types/document';

interface EmbeddingStatusCardProps {
  document: Document;
  onRegenerate?: () => void;
}

/**
 * Get icon for embedding status
 */
function getEmbeddingIcon(status?: string) {
  switch (status) {
    case 'completed':
      return CheckCircle2;
    case 'failed':
      return XCircle;
    case 'in_progress':
      return RefreshCw;
    case 'not_started':
    default:
      return Sparkles;
  }
}

/**
 * Get status color
 */
function getEmbeddingColor(status?: string): string {
  switch (status) {
    case 'completed':
      return 'text-emerald-600';
    case 'failed':
      return 'text-red-600';
    case 'in_progress':
      return 'text-purple-600';
    case 'not_started':
    default:
      return 'text-slate-600';
  }
}

/**
 * Embedding Status Card Component
 * 
 * Displays:
 * - Current embedding status
 * - Embedding statistics (chunk count, coverage)
 * - Embedding model information
 * - Related jobs (if available)
 * - Regenerate action
 * 
 * @example
 * ```tsx
 * <EmbeddingStatusCard 
 *   document={document}
 *   onRegenerate={() => handleRegenerate()}
 * />
 * ```
 */
export function EmbeddingStatusCard({
  document,
  onRegenerate,
}: EmbeddingStatusCardProps) {
  const embeddingStatus = document.embedding_status || 'not_started';
  const EmbeddingIcon = getEmbeddingIcon(embeddingStatus);
  const statusColor = getEmbeddingColor(embeddingStatus);

  // Find embedding job if available
  const embeddingJob = document.processing_jobs?.find(
    (job) => job.job_type === 'embedding_generation'
  );

  // Calculate chunk statistics
  const totalChunks = document.chunks?.length || document.chunk_count || 0;
  const chunksWithEmbeddings = document.chunks?.filter(c => c.embedding_vector !== null).length || 0;
  const embeddingCoverage = totalChunks > 0 ? (chunksWithEmbeddings / totalChunks) * 100 : 0;

  const showRegenerateButton = 
    embeddingStatus === 'failed' || 
    embeddingStatus === 'completed';

  const canGenerateEmbeddings = document.processing_status === 'parsed';

  return (
    <Card>
      <CardContent className="p-6 space-y-4">
        {/* Header */}
        <div className="flex items-start justify-between">
          <div className="flex items-center gap-3">
            <div className={`p-2 rounded-lg bg-slate-100 dark:bg-slate-800 ${statusColor}`}>
              <EmbeddingIcon className={`h-5 w-5 ${embeddingStatus === 'in_progress' ? 'animate-spin' : ''}`} />
            </div>
            <div>
              <h3 className="text-lg font-semibold text-slate-900 dark:text-slate-100">
                Embedding Status
              </h3>
              <p className="text-sm text-slate-600 dark:text-slate-400">
                Vector embeddings for semantic search
              </p>
            </div>
          </div>
          {embeddingStatus !== 'not_started' && (
            <StatusBadge status={embeddingStatus} type="embedding" />
          )}
        </div>

        {/* Status Details */}
        <div className="space-y-3 pt-2">
          {/* Completed State */}
          {embeddingStatus === 'completed' && (
            <div className="bg-emerald-50 dark:bg-emerald-950/30 border border-emerald-200 dark:border-emerald-800 rounded-lg p-4">
              <div className="flex items-start gap-3">
                <CheckCircle2 className="h-5 w-5 text-emerald-600 flex-shrink-0 mt-0.5" />
                <div className="flex-1">
                  <p className="font-medium text-emerald-900 dark:text-emerald-100">
                    Embeddings Generated
                  </p>
                  <p className="text-sm text-emerald-700 dark:text-emerald-300 mt-1">
                    Document is fully embedded and searchable.
                  </p>
                  {embeddingJob?.completed_at && (
                    <p className="text-xs text-emerald-600 dark:text-emerald-400 mt-2">
                      Completed {formatRelativeTime(embeddingJob.completed_at)}
                    </p>
                  )}
                </div>
              </div>
            </div>
          )}

          {/* Failed State */}
          {embeddingStatus === 'failed' && (
            <div className="bg-red-50 dark:bg-red-950/30 border border-red-200 dark:border-red-800 rounded-lg p-4">
              <div className="flex items-start gap-3">
                <XCircle className="h-5 w-5 text-red-600 flex-shrink-0 mt-0.5" />
                <div className="flex-1">
                  <p className="font-medium text-red-900 dark:text-red-100">
                    Embedding Generation Failed
                  </p>
                  {embeddingJob?.error_message && (
                    <p className="text-sm text-red-700 dark:text-red-300 mt-1 font-mono">
                      {embeddingJob.error_message}
                    </p>
                  )}
                  <p className="text-sm text-red-600 dark:text-red-400 mt-2">
                    Try regenerating embeddings or contact support if the issue persists.
                  </p>
                </div>
              </div>
            </div>
          )}

          {/* In Progress State */}
          {embeddingStatus === 'in_progress' && (
            <div className="bg-purple-50 dark:bg-purple-950/30 border border-purple-200 dark:border-purple-800 rounded-lg p-4">
              <div className="flex items-start gap-3">
                <RefreshCw className="h-5 w-5 text-purple-600 flex-shrink-0 mt-0.5 animate-spin" />
                <div className="flex-1">
                  <p className="font-medium text-purple-900 dark:text-purple-100">
                    Generating Embeddings
                  </p>
                  <p className="text-sm text-purple-700 dark:text-purple-300 mt-1">
                    Creating vector embeddings for {totalChunks} chunks.
                  </p>
                  {embeddingJob?.progress_percent !== undefined && (
                    <div className="mt-3">
                      <div className="flex items-center justify-between text-xs text-purple-700 dark:text-purple-300 mb-1">
                        <span>Progress</span>
                        <span>{embeddingJob.progress_percent}%</span>
                      </div>
                      <div className="h-2 bg-purple-200 dark:bg-purple-900 rounded-full overflow-hidden">
                        <div
                          className="h-full bg-purple-600 dark:bg-purple-400 transition-all duration-300"
                          style={{ width: `${embeddingJob.progress_percent}%` }}
                        />
                      </div>
                    </div>
                  )}
                </div>
              </div>
            </div>
          )}

          {/* Not Started State */}
          {embeddingStatus === 'not_started' && (
            <div className="bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-lg p-4">
              <div className="flex items-start gap-3">
                <Clock className="h-5 w-5 text-slate-600 dark:text-slate-400 flex-shrink-0 mt-0.5" />
                <div className="flex-1">
                  <p className="font-medium text-slate-900 dark:text-slate-100">
                    {canGenerateEmbeddings ? 'Ready for Embedding' : 'Awaiting Processing'}
                  </p>
                  <p className="text-sm text-slate-600 dark:text-slate-400 mt-1">
                    {canGenerateEmbeddings 
                      ? 'Document is parsed and ready to generate embeddings.'
                      : 'Document must be processed before embeddings can be generated.'}
                  </p>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Embedding Statistics */}
        {totalChunks > 0 && (embeddingStatus === 'completed' || embeddingStatus === 'in_progress') && (
          <div className="pt-3 border-t border-slate-200 dark:border-slate-800">
            <h4 className="text-sm font-semibold text-slate-900 dark:text-slate-100 mb-3 flex items-center gap-2">
              <TrendingUp className="h-4 w-4" />
              Statistics
            </h4>
            <dl className="grid grid-cols-2 gap-3 text-sm">
              <div>
                <dt className="text-slate-600 dark:text-slate-400">Total Chunks</dt>
                <dd className="text-lg font-semibold text-slate-900 dark:text-slate-100 mt-0.5">
                  {totalChunks}
                </dd>
              </div>
              <div>
                <dt className="text-slate-600 dark:text-slate-400">With Embeddings</dt>
                <dd className="text-lg font-semibold text-slate-900 dark:text-slate-100 mt-0.5">
                  {chunksWithEmbeddings}
                </dd>
              </div>
              <div className="col-span-2">
                <dt className="text-slate-600 dark:text-slate-400 mb-2">Coverage</dt>
                <div className="h-2 bg-slate-200 dark:bg-slate-800 rounded-full overflow-hidden">
                  <div
                    className="h-full bg-emerald-600 dark:bg-emerald-400 transition-all duration-300"
                    style={{ width: `${embeddingCoverage}%` }}
                  />
                </div>
                <dd className="text-xs text-slate-600 dark:text-slate-400 mt-1">
                  {embeddingCoverage.toFixed(1)}% embedded
                </dd>
              </div>
            </dl>
          </div>
        )}

        {/* Job Details */}
        {embeddingJob && (
          <div className="pt-3 border-t border-slate-200 dark:border-slate-800">
            <h4 className="text-sm font-semibold text-slate-900 dark:text-slate-100 mb-3">
              Job Details
            </h4>
            <dl className="grid grid-cols-2 gap-3 text-sm">
              <div>
                <dt className="text-slate-600 dark:text-slate-400">Job ID</dt>
                <dd className="font-mono text-slate-900 dark:text-slate-100 mt-0.5">
                  #{embeddingJob.job_id}
                </dd>
              </div>
              {embeddingJob.started_at && (
                <div>
                  <dt className="text-slate-600 dark:text-slate-400">Started</dt>
                  <dd className="text-slate-900 dark:text-slate-100 mt-0.5">
                    {formatRelativeTime(embeddingJob.started_at)}
                  </dd>
                </div>
              )}
              {embeddingJob.completed_at && embeddingJob.started_at && (
                <div>
                  <dt className="text-slate-600 dark:text-slate-400">Duration</dt>
                  <dd className="text-slate-900 dark:text-slate-100 mt-0.5">
                    {getDuration(embeddingJob.started_at, embeddingJob.completed_at)}
                  </dd>
                </div>
              )}
              {embeddingJob.retry_count > 0 && (
                <div>
                  <dt className="text-slate-600 dark:text-slate-400">Retry Count</dt>
                  <dd className="text-slate-900 dark:text-slate-100 mt-0.5">
                    {embeddingJob.retry_count} / {embeddingJob.max_retries}
                  </dd>
                </div>
              )}
            </dl>
          </div>
        )}

        {/* Regenerate Button */}
        {showRegenerateButton && onRegenerate && (
          <div className="pt-3 border-t border-slate-200 dark:border-slate-800">
            <Button
              variant="outline"
              size="sm"
              onClick={onRegenerate}
              className="w-full"
            >
              <RefreshCw className="h-4 w-4 mr-2" />
              Regenerate Embeddings
            </Button>
          </div>
        )}

        {/* Generate Button (if not started) */}
        {embeddingStatus === 'not_started' && canGenerateEmbeddings && onRegenerate && (
          <div className="pt-3 border-t border-slate-200 dark:border-slate-800">
            <Button
              onClick={onRegenerate}
              size="sm"
              className="w-full"
            >
              <Sparkles className="h-4 w-4 mr-2" />
              Generate Embeddings
            </Button>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
