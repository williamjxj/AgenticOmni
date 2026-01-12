/**
 * Skeleton loading components for better UX
 * Feature: 005-view-embedded-docs
 */

import { cn } from '@/lib/utils';

// ============================================================================
// Base Skeleton Component
// ============================================================================

interface SkeletonProps extends React.HTMLAttributes<HTMLDivElement> {
  variant?: 'default' | 'circular' | 'rectangular';
}

/**
 * Base skeleton component with shimmer animation
 */
export function Skeleton({
  className,
  variant = 'default',
  ...props
}: SkeletonProps) {
  return (
    <div
      className={cn(
        'animate-pulse bg-slate-200 dark:bg-slate-800',
        variant === 'circular' && 'rounded-full',
        variant === 'rectangular' && 'rounded-md',
        variant === 'default' && 'rounded-md',
        className
      )}
      {...props}
    />
  );
}

// ============================================================================
// Document-Specific Skeletons
// ============================================================================

/**
 * Skeleton for document card in list view
 */
export function DocumentCardSkeleton() {
  return (
    <div className="border rounded-lg p-6 space-y-4">
      <div className="flex items-start justify-between">
        <div className="flex gap-4 flex-1">
          {/* Icon skeleton */}
          <Skeleton className="h-8 w-8 rounded-md flex-shrink-0" />
          
          <div className="flex-1 space-y-3">
            {/* Filename skeleton */}
            <Skeleton className="h-5 w-3/4" />
            
            {/* Metadata row */}
            <div className="flex gap-4">
              <Skeleton className="h-4 w-16" />
              <Skeleton className="h-4 w-20" />
              <Skeleton className="h-4 w-24" />
            </div>
            
            {/* Date skeleton */}
            <Skeleton className="h-3 w-32" />
          </div>
        </div>
        
        {/* Status badge and action button */}
        <div className="flex items-center gap-3">
          <Skeleton className="h-6 w-20 rounded-full" />
          <Skeleton className="h-8 w-8 rounded-md" />
        </div>
      </div>
    </div>
  );
}

/**
 * Skeleton for document list (multiple cards)
 */
export function DocumentListSkeleton({ count = 5 }: { count?: number }) {
  return (
    <div className="space-y-4">
      {Array.from({ length: count }).map((_, i) => (
        <DocumentCardSkeleton key={i} />
      ))}
    </div>
  );
}

/**
 * Skeleton for document detail header
 */
export function DocumentHeaderSkeleton() {
  return (
    <div className="space-y-4">
      {/* Title and filename */}
      <div className="space-y-2">
        <Skeleton className="h-8 w-2/3" />
        <Skeleton className="h-5 w-1/2" />
      </div>
      
      {/* Metadata grid */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {Array.from({ length: 4 }).map((_, i) => (
          <div key={i} className="space-y-2">
            <Skeleton className="h-4 w-20" />
            <Skeleton className="h-5 w-full" />
          </div>
        ))}
      </div>
    </div>
  );
}

/**
 * Skeleton for status cards (processing, embedding)
 */
export function StatusCardSkeleton() {
  return (
    <div className="border rounded-lg p-6 space-y-4">
      <div className="flex items-center justify-between">
        <Skeleton className="h-6 w-32" />
        <Skeleton className="h-5 w-20 rounded-full" />
      </div>
      
      <div className="space-y-2">
        <Skeleton className="h-4 w-full" />
        <Skeleton className="h-4 w-3/4" />
      </div>
    </div>
  );
}

/**
 * Skeleton for text preview
 */
export function TextPreviewSkeleton() {
  return (
    <div className="border rounded-lg p-6 space-y-4">
      <Skeleton className="h-6 w-32" />
      
      <div className="space-y-2">
        <Skeleton className="h-4 w-full" />
        <Skeleton className="h-4 w-full" />
        <Skeleton className="h-4 w-5/6" />
        <Skeleton className="h-4 w-full" />
        <Skeleton className="h-4 w-4/5" />
        <Skeleton className="h-4 w-full" />
        <Skeleton className="h-4 w-3/4" />
      </div>
    </div>
  );
}

/**
 * Skeleton for chunk list
 */
export function ChunkListSkeleton({ count = 3 }: { count?: number }) {
  return (
    <div className="space-y-3">
      {Array.from({ length: count }).map((_, i) => (
        <div key={i} className="border rounded-lg p-4 space-y-3">
          <div className="flex items-center justify-between">
            <Skeleton className="h-4 w-24" />
            <Skeleton className="h-5 w-16 rounded-full" />
          </div>
          
          <div className="space-y-2">
            <Skeleton className="h-3 w-full" />
            <Skeleton className="h-3 w-full" />
            <Skeleton className="h-3 w-2/3" />
          </div>
          
          <div className="flex gap-3">
            <Skeleton className="h-3 w-20" />
            <Skeleton className="h-3 w-16" />
          </div>
        </div>
      ))}
    </div>
  );
}

/**
 * Skeleton for statistics cards
 */
export function StatisticsCardSkeleton() {
  return (
    <div className="border rounded-lg p-6 space-y-4">
      <Skeleton className="h-6 w-40" />
      
      <div className="grid grid-cols-2 gap-4">
        {Array.from({ length: 4 }).map((_, i) => (
          <div key={i} className="space-y-2">
            <Skeleton className="h-3 w-24" />
            <Skeleton className="h-7 w-16" />
          </div>
        ))}
      </div>
    </div>
  );
}

/**
 * Skeleton for page header with actions
 */
export function PageHeaderSkeleton() {
  return (
    <div className="flex items-center justify-between">
      <div className="space-y-2">
        <Skeleton className="h-8 w-48" />
        <Skeleton className="h-4 w-64" />
      </div>
      
      <div className="flex gap-2">
        <Skeleton className="h-10 w-24" />
        <Skeleton className="h-10 w-32" />
      </div>
    </div>
  );
}

/**
 * Skeleton for filter bar
 */
export function FilterBarSkeleton() {
  return (
    <div className="flex flex-wrap gap-3">
      <Skeleton className="h-10 w-40" />
      <Skeleton className="h-10 w-32" />
      <Skeleton className="h-10 w-36" />
      <Skeleton className="h-10 w-28" />
    </div>
  );
}

/**
 * Skeleton for pagination controls
 */
export function PaginationSkeleton() {
  return (
    <div className="flex justify-center items-center gap-2">
      <Skeleton className="h-10 w-24" />
      <Skeleton className="h-10 w-32" />
      <Skeleton className="h-10 w-24" />
    </div>
  );
}

// ============================================================================
// Full Page Skeletons
// ============================================================================

/**
 * Skeleton for entire documents list page
 */
export function DocumentsPageSkeleton() {
  return (
    <div className="space-y-8">
      <PageHeaderSkeleton />
      <FilterBarSkeleton />
      <DocumentListSkeleton count={5} />
      <PaginationSkeleton />
    </div>
  );
}

/**
 * Skeleton for entire document detail page
 */
export function DocumentDetailPageSkeleton() {
  return (
    <div className="space-y-8">
      <DocumentHeaderSkeleton />
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <StatusCardSkeleton />
        <StatusCardSkeleton />
      </div>
      
      <TextPreviewSkeleton />
      
      <div className="space-y-4">
        <Skeleton className="h-6 w-32" />
        <ChunkListSkeleton count={3} />
      </div>
    </div>
  );
}
