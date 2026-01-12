/**
 * Status Badge Component
 * Displays processing, embedding, and OCR status with colors and icons
 * Feature: 005-view-embedded-docs / User Story 1
 */

import { CheckCircle2, Clock, XCircle, Loader2, AlertCircle } from 'lucide-react';
import { cn } from '@/lib/utils';
import type { ProcessingStatus, EmbeddingStatus, OCRStatus } from '@/lib/types/document';

type StatusType = 'processing' | 'embedding' | 'ocr';
type StatusValue = ProcessingStatus | EmbeddingStatus | OCRStatus | string;

interface StatusBadgeProps {
  status: StatusValue;
  type?: StatusType;
  size?: 'sm' | 'md' | 'lg';
  className?: string;
}

interface StatusConfig {
  label: string;
  color: string;
  icon: React.ComponentType<{ className?: string }>;
}

/**
 * Get status configuration for processing status
 */
function getProcessingStatusConfig(status: string): StatusConfig {
  const configs: Record<string, StatusConfig> = {
    uploaded: {
      label: 'Uploaded',
      color: 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200',
      icon: Clock,
    },
    pending: {
      label: 'Pending',
      color: 'bg-slate-100 text-slate-800 dark:bg-slate-800 dark:text-slate-200',
      icon: Clock,
    },
    parsing: {
      label: 'Processing...',
      color: 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200',
      icon: Loader2,
    },
    parsed: {
      label: 'Ready',
      color: 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200',
      icon: CheckCircle2,
    },
    failed: {
      label: 'Failed',
      color: 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200',
      icon: XCircle,
    },
  };

  return configs[status] || configs.uploaded;
}

/**
 * Get status configuration for embedding status
 */
function getEmbeddingStatusConfig(status: string): StatusConfig {
  const configs: Record<string, StatusConfig> = {
    not_started: {
      label: 'Not Started',
      color: 'bg-slate-100 text-slate-800 dark:bg-slate-800 dark:text-slate-300',
      icon: Clock,
    },
    in_progress: {
      label: 'Generating...',
      color: 'bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-200',
      icon: Loader2,
    },
    completed: {
      label: 'Embedded',
      color: 'bg-emerald-100 text-emerald-800 dark:bg-emerald-900 dark:text-emerald-200',
      icon: CheckCircle2,
    },
    failed: {
      label: 'Failed',
      color: 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200',
      icon: XCircle,
    },
  };

  return configs[status] || configs.not_started;
}

/**
 * Get status configuration for OCR status
 */
function getOCRStatusConfig(status: string): StatusConfig {
  const configs: Record<string, StatusConfig> = {
    not_started: {
      label: 'No OCR',
      color: 'bg-slate-100 text-slate-800 dark:bg-slate-800 dark:text-slate-300',
      icon: Clock,
    },
    in_progress: {
      label: 'OCR Running...',
      color: 'bg-amber-100 text-amber-800 dark:bg-amber-900 dark:text-amber-200',
      icon: Loader2,
    },
    completed: {
      label: 'OCR Complete',
      color: 'bg-teal-100 text-teal-800 dark:bg-teal-900 dark:text-teal-200',
      icon: CheckCircle2,
    },
    failed: {
      label: 'OCR Failed',
      color: 'bg-orange-100 text-orange-800 dark:bg-orange-900 dark:text-orange-200',
      icon: AlertCircle,
    },
  };

  return configs[status] || configs.not_started;
}

/**
 * Get size classes for badge
 */
function getSizeClasses(size: 'sm' | 'md' | 'lg'): string {
  const sizes = {
    sm: 'px-2 py-0.5 text-xs',
    md: 'px-3 py-1 text-sm',
    lg: 'px-4 py-1.5 text-base',
  };
  return sizes[size];
}

/**
 * Get icon size classes
 */
function getIconSize(size: 'sm' | 'md' | 'lg'): string {
  const sizes = {
    sm: 'h-3 w-3',
    md: 'h-4 w-4',
    lg: 'h-5 w-5',
  };
  return sizes[size];
}

/**
 * Status Badge Component
 * 
 * @example
 * ```tsx
 * <StatusBadge status="parsed" type="processing" />
 * <StatusBadge status="completed" type="embedding" size="sm" />
 * <StatusBadge status="in_progress" type="ocr" />
 * ```
 */
export function StatusBadge({
  status,
  type = 'processing',
  size = 'md',
  className,
}: StatusBadgeProps) {
  // Get appropriate config based on type
  let config: StatusConfig;
  switch (type) {
    case 'embedding':
      config = getEmbeddingStatusConfig(status);
      break;
    case 'ocr':
      config = getOCRStatusConfig(status);
      break;
    case 'processing':
    default:
      config = getProcessingStatusConfig(status);
      break;
  }

  const Icon = config.icon;
  const isAnimated = status === 'parsing' || status === 'in_progress';

  return (
    <span
      className={cn(
        'inline-flex items-center gap-1.5 rounded-full font-medium whitespace-nowrap',
        config.color,
        getSizeClasses(size),
        className
      )}
    >
      <Icon 
        className={cn(
          getIconSize(size),
          isAnimated && 'animate-spin'
        )} 
      />
      {config.label}
    </span>
  );
}

/**
 * Status badge with tooltip explaining the status
 */
export function StatusBadgeWithTooltip({
  status,
  type = 'processing',
  size = 'md',
  className,
}: StatusBadgeProps) {
  const tooltips: Record<StatusType, Record<string, string>> = {
    processing: {
      uploaded: 'Document uploaded and awaiting processing',
      pending: 'Document is queued for processing',
      parsing: 'Document is being parsed and extracted',
      parsed: 'Document successfully processed and ready to search',
      failed: 'Document processing failed. Check logs for details.',
    },
    embedding: {
      not_started: 'Embeddings have not been generated yet',
      in_progress: 'Vector embeddings are being generated',
      completed: 'Vector embeddings generated successfully',
      failed: 'Embedding generation failed. Try regenerating.',
    },
    ocr: {
      not_started: 'OCR processing not started',
      in_progress: 'Optical Character Recognition in progress',
      completed: 'Text successfully extracted via OCR',
      failed: 'OCR processing failed',
    },
  };

  const tooltip = tooltips[type][status] || '';

  return (
    <div className="group relative inline-flex">
      <StatusBadge 
        status={status} 
        type={type} 
        size={size} 
        className={className} 
      />
      
      {tooltip && (
        <div className="absolute bottom-full left-1/2 -translate-x-1/2 mb-2 px-3 py-2 bg-slate-900 dark:bg-slate-100 text-white dark:text-slate-900 text-xs rounded-lg opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all duration-200 whitespace-nowrap z-10 pointer-events-none">
          {tooltip}
          <div className="absolute top-full left-1/2 -translate-x-1/2 -mt-1 border-4 border-transparent border-t-slate-900 dark:border-t-slate-100" />
        </div>
      )}
    </div>
  );
}
