/**
 * Processing Status Card Component
 * Shows document processing status and related jobs
 * Feature: 005-view-embedded-docs / User Story 2
 */

import { CheckCircle2, XCircle, Clock, AlertCircle, RefreshCw } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import { StatusBadge } from './status-badge';
import { formatDate, formatRelativeTime, getDuration } from '@/lib/utils/date';
import type { Document, ProcessingJob } from '@/lib/types/document';

interface ProcessingStatusCardProps {
  document: Document;
  onReprocess?: () => void;
}

/**
 * Get icon for processing status
 */
function getStatusIcon(status: string) {
  switch (status) {
    case 'parsed':
      return CheckCircle2;
    case 'failed':
      return XCircle;
    case 'parsing':
      return RefreshCw;
    case 'uploaded':
    case 'pending':
    default:
      return Clock;
  }
}

/**
 * Get status color
 */
function getStatusColor(status: string): string {
  switch (status) {
    case 'parsed':
      return 'text-green-600';
    case 'failed':
      return 'text-red-600';
    case 'parsing':
      return 'text-yellow-600';
    case 'uploaded':
    case 'pending':
    default:
      return 'text-slate-600';
  }
}

/**
 * Processing Status Card Component
 * 
 * Displays:
 * - Current processing status
 * - Processing timeline
 * - Related jobs (if available)
 * - Error messages (if failed)
 * - Reprocess action
 * 
 * @example
 * ```tsx
 * <ProcessingStatusCard 
 *   document={document} 
 *   onReprocess={() => handleReprocess()} 
 * />
 * ```
 */
export function ProcessingStatusCard({
  document,
  onReprocess,
}: ProcessingStatusCardProps) {
  const StatusIcon = getStatusIcon(document.processing_status);
  const statusColor = getStatusColor(document.processing_status);

  // Find parsing job if available
  const parsingJob = document.processing_jobs?.find(
    (job) => job.job_type === 'parse_document'
  );

  const showReprocessButton = 
    document.processing_status === 'failed' || 
    document.processing_status === 'parsed';

  return (
    <Card>
      <CardContent className="p-6 space-y-4">
        {/* Header */}
        <div className="flex items-start justify-between">
          <div className="flex items-center gap-3">
            <div className={`p-2 rounded-lg bg-slate-100 dark:bg-slate-800 ${statusColor}`}>
              <StatusIcon className={`h-5 w-5 ${document.processing_status === 'parsing' ? 'animate-spin' : ''}`} />
            </div>
            <div>
              <h3 className="text-lg font-semibold text-slate-900 dark:text-slate-100">
                Processing Status
              </h3>
              <p className="text-sm text-slate-600 dark:text-slate-400">
                Document parsing and extraction
              </p>
            </div>
          </div>
          <StatusBadge status={document.processing_status} type="processing" />
        </div>

        {/* Status Details */}
        <div className="space-y-3 pt-2">
          {/* Success State */}
          {document.processing_status === 'parsed' && (
            <div className="bg-green-50 dark:bg-green-950/30 border border-green-200 dark:border-green-800 rounded-lg p-4">
              <div className="flex items-start gap-3">
                <CheckCircle2 className="h-5 w-5 text-green-600 flex-shrink-0 mt-0.5" />
                <div className="flex-1">
                  <p className="font-medium text-green-900 dark:text-green-100">
                    Processing Complete
                  </p>
                  <p className="text-sm text-green-700 dark:text-green-300 mt-1">
                    Document successfully parsed and ready for embedding generation.
                  </p>
                  {parsingJob?.completed_at && (
                    <p className="text-xs text-green-600 dark:text-green-400 mt-2">
                      Completed {formatRelativeTime(parsingJob.completed_at)}
                    </p>
                  )}
                </div>
              </div>
            </div>
          )}

          {/* Failed State */}
          {document.processing_status === 'failed' && (
            <div className="bg-red-50 dark:bg-red-950/30 border border-red-200 dark:border-red-800 rounded-lg p-4">
              <div className="flex items-start gap-3">
                <XCircle className="h-5 w-5 text-red-600 flex-shrink-0 mt-0.5" />
                <div className="flex-1">
                  <p className="font-medium text-red-900 dark:text-red-100">
                    Processing Failed
                  </p>
                  {parsingJob?.error_message && (
                    <p className="text-sm text-red-700 dark:text-red-300 mt-1 font-mono">
                      {parsingJob.error_message}
                    </p>
                  )}
                  <p className="text-sm text-red-600 dark:text-red-400 mt-2">
                    Try reprocessing the document or contact support if the issue persists.
                  </p>
                </div>
              </div>
            </div>
          )}

          {/* In Progress State */}
          {document.processing_status === 'parsing' && (
            <div className="bg-yellow-50 dark:bg-yellow-950/30 border border-yellow-200 dark:border-yellow-800 rounded-lg p-4">
              <div className="flex items-start gap-3">
                <RefreshCw className="h-5 w-5 text-yellow-600 flex-shrink-0 mt-0.5 animate-spin" />
                <div className="flex-1">
                  <p className="font-medium text-yellow-900 dark:text-yellow-100">
                    Processing In Progress
                  </p>
                  <p className="text-sm text-yellow-700 dark:text-yellow-300 mt-1">
                    Your document is being parsed and extracted. This may take a few moments.
                  </p>
                  {parsingJob?.progress_percent !== undefined && (
                    <div className="mt-3">
                      <div className="flex items-center justify-between text-xs text-yellow-700 dark:text-yellow-300 mb-1">
                        <span>Progress</span>
                        <span>{parsingJob.progress_percent}%</span>
                      </div>
                      <div className="h-2 bg-yellow-200 dark:bg-yellow-900 rounded-full overflow-hidden">
                        <div
                          className="h-full bg-yellow-600 dark:bg-yellow-400 transition-all duration-300"
                          style={{ width: `${parsingJob.progress_percent}%` }}
                        />
                      </div>
                    </div>
                  )}
                </div>
              </div>
            </div>
          )}

          {/* Pending State */}
          {(document.processing_status === 'pending' || document.processing_status === 'uploaded') && (
            <div className="bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-lg p-4">
              <div className="flex items-start gap-3">
                <Clock className="h-5 w-5 text-slate-600 dark:text-slate-400 flex-shrink-0 mt-0.5" />
                <div className="flex-1">
                  <p className="font-medium text-slate-900 dark:text-slate-100">
                    Queued for Processing
                  </p>
                  <p className="text-sm text-slate-600 dark:text-slate-400 mt-1">
                    Your document is in the processing queue and will be handled shortly.
                  </p>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Job Details */}
        {parsingJob && (
          <div className="pt-3 border-t border-slate-200 dark:border-slate-800">
            <h4 className="text-sm font-semibold text-slate-900 dark:text-slate-100 mb-3">
              Job Details
            </h4>
            <dl className="grid grid-cols-2 gap-3 text-sm">
              <div>
                <dt className="text-slate-600 dark:text-slate-400">Job ID</dt>
                <dd className="font-mono text-slate-900 dark:text-slate-100 mt-0.5">
                  #{parsingJob.job_id}
                </dd>
              </div>
              {parsingJob.started_at && (
                <div>
                  <dt className="text-slate-600 dark:text-slate-400">Started</dt>
                  <dd className="text-slate-900 dark:text-slate-100 mt-0.5">
                    {formatRelativeTime(parsingJob.started_at)}
                  </dd>
                </div>
              )}
              {parsingJob.completed_at && parsingJob.started_at && (
                <div>
                  <dt className="text-slate-600 dark:text-slate-400">Duration</dt>
                  <dd className="text-slate-900 dark:text-slate-100 mt-0.5">
                    {getDuration(parsingJob.started_at, parsingJob.completed_at)}
                  </dd>
                </div>
              )}
              {parsingJob.retry_count > 0 && (
                <div>
                  <dt className="text-slate-600 dark:text-slate-400">Retry Count</dt>
                  <dd className="text-slate-900 dark:text-slate-100 mt-0.5">
                    {parsingJob.retry_count} / {parsingJob.max_retries}
                  </dd>
                </div>
              )}
            </dl>
          </div>
        )}

        {/* Reprocess Button */}
        {showReprocessButton && onReprocess && (
          <div className="pt-3 border-t border-slate-200 dark:border-slate-800">
            <Button
              variant="outline"
              size="sm"
              onClick={onReprocess}
              className="w-full"
            >
              <RefreshCw className="h-4 w-4 mr-2" />
              Reprocess Document
            </Button>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
