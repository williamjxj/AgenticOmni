/**
 * Pagination Component
 * Handles page navigation for document lists
 * Feature: 005-view-embedded-docs / User Story 1
 */

import { ChevronLeft, ChevronRight, ChevronsLeft, ChevronsRight } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { cn } from '@/lib/utils';

interface PaginationProps {
  currentPage: number;
  totalPages: number;
  onPageChange: (page: number) => void;
  totalItems?: number;
  pageSize?: number;
  showFirstLast?: boolean;
  showPageInfo?: boolean;
  className?: string;
}

/**
 * Generate page numbers to display
 * Shows ellipsis for large page counts
 * 
 * @example
 * getPageNumbers(5, 10) // [1, "...", 4, 5, 6, "...", 10]
 */
function getPageNumbers(currentPage: number, totalPages: number): (number | string)[] {
  if (totalPages <= 7) {
    // Show all pages if 7 or fewer
    return Array.from({ length: totalPages }, (_, i) => i + 1);
  }

  // Always show first page, last page, and pages around current page
  const pages: (number | string)[] = [];

  if (currentPage <= 3) {
    // Near the start
    pages.push(1, 2, 3, 4, '...', totalPages);
  } else if (currentPage >= totalPages - 2) {
    // Near the end
    pages.push(1, '...', totalPages - 3, totalPages - 2, totalPages - 1, totalPages);
  } else {
    // In the middle
    pages.push(1, '...', currentPage - 1, currentPage, currentPage + 1, '...', totalPages);
  }

  return pages;
}

/**
 * Pagination Component
 * 
 * @example
 * ```tsx
 * <Pagination
 *   currentPage={page}
 *   totalPages={totalPages}
 *   onPageChange={(p) => setPage(p)}
 *   totalItems={100}
 *   pageSize={20}
 * />
 * ```
 */
export function Pagination({
  currentPage,
  totalPages,
  onPageChange,
  totalItems,
  pageSize,
  showFirstLast = true,
  showPageInfo = true,
  className,
}: PaginationProps) {
  // Don't render if no pages
  if (totalPages <= 0) return null;

  const pages = getPageNumbers(currentPage, totalPages);

  const canGoPrevious = currentPage > 1;
  const canGoNext = currentPage < totalPages;

  return (
    <div className={cn('flex flex-col sm:flex-row items-center justify-between gap-4', className)}>
      {/* Page info */}
      {showPageInfo && totalItems !== undefined && pageSize !== undefined && (
        <div className="text-sm text-slate-600 dark:text-slate-400">
          Showing{' '}
          <span className="font-medium">
            {Math.min((currentPage - 1) * pageSize + 1, totalItems)}
          </span>
          {' '}-{' '}
          <span className="font-medium">
            {Math.min(currentPage * pageSize, totalItems)}
          </span>
          {' '}of{' '}
          <span className="font-medium">{totalItems}</span>
          {' '}documents
        </div>
      )}

      {/* Page controls */}
      <div className="flex items-center gap-1">
        {/* First page button */}
        {showFirstLast && (
          <Button
            variant="outline"
            size="sm"
            onClick={() => onPageChange(1)}
            disabled={!canGoPrevious}
            className="h-9 w-9 p-0"
            title="First page"
          >
            <ChevronsLeft className="h-4 w-4" />
          </Button>
        )}

        {/* Previous page button */}
        <Button
          variant="outline"
          size="sm"
          onClick={() => onPageChange(currentPage - 1)}
          disabled={!canGoPrevious}
          className="h-9 w-9 p-0 sm:w-auto sm:px-3"
          title="Previous page"
        >
          <ChevronLeft className="h-4 w-4" />
          <span className="hidden sm:inline ml-1">Previous</span>
        </Button>

        {/* Page number buttons */}
        <div className="flex items-center gap-1">
          {pages.map((page, index) => {
            if (page === '...') {
              return (
                <span
                  key={`ellipsis-${index}`}
                  className="flex h-9 w-9 items-center justify-center text-slate-500"
                >
                  ...
                </span>
              );
            }

            const pageNum = page as number;
            const isCurrentPage = pageNum === currentPage;

            return (
              <Button
                key={pageNum}
                variant={isCurrentPage ? 'default' : 'outline'}
                size="sm"
                onClick={() => onPageChange(pageNum)}
                className={cn(
                  'h-9 w-9 p-0',
                  isCurrentPage && 'pointer-events-none'
                )}
                aria-label={`Page ${pageNum}`}
                aria-current={isCurrentPage ? 'page' : undefined}
              >
                {pageNum}
              </Button>
            );
          })}
        </div>

        {/* Next page button */}
        <Button
          variant="outline"
          size="sm"
          onClick={() => onPageChange(currentPage + 1)}
          disabled={!canGoNext}
          className="h-9 w-9 p-0 sm:w-auto sm:px-3"
          title="Next page"
        >
          <span className="hidden sm:inline mr-1">Next</span>
          <ChevronRight className="h-4 w-4" />
        </Button>

        {/* Last page button */}
        {showFirstLast && (
          <Button
            variant="outline"
            size="sm"
            onClick={() => onPageChange(totalPages)}
            disabled={!canGoNext}
            className="h-9 w-9 p-0"
            title="Last page"
          >
            <ChevronsRight className="h-4 w-4" />
          </Button>
        )}
      </div>
    </div>
  );
}

/**
 * Simple Pagination Component
 * Simplified version with just previous/next and page counter
 * 
 * @example
 * ```tsx
 * <SimplePagination
 *   currentPage={page}
 *   totalPages={totalPages}
 *   onPageChange={(p) => setPage(p)}
 * />
 * ```
 */
export function SimplePagination({
  currentPage,
  totalPages,
  onPageChange,
  className,
}: Pick<PaginationProps, 'currentPage' | 'totalPages' | 'onPageChange' | 'className'>) {
  if (totalPages <= 0) return null;

  const canGoPrevious = currentPage > 1;
  const canGoNext = currentPage < totalPages;

  return (
    <div className={cn('flex items-center justify-center gap-3', className)}>
      <Button
        variant="outline"
        size="sm"
        onClick={() => onPageChange(currentPage - 1)}
        disabled={!canGoPrevious}
      >
        <ChevronLeft className="h-4 w-4 mr-1" />
        Previous
      </Button>

      <span className="text-sm text-slate-600 dark:text-slate-400 min-w-[100px] text-center">
        Page {currentPage} of {totalPages}
      </span>

      <Button
        variant="outline"
        size="sm"
        onClick={() => onPageChange(currentPage + 1)}
        disabled={!canGoNext}
      >
        Next
        <ChevronRight className="h-4 w-4 ml-1" />
      </Button>
    </div>
  );
}

/**
 * Compact Pagination Component
 * Minimalist version for small spaces
 */
export function CompactPagination({
  currentPage,
  totalPages,
  onPageChange,
  className,
}: Pick<PaginationProps, 'currentPage' | 'totalPages' | 'onPageChange' | 'className'>) {
  if (totalPages <= 0) return null;

  return (
    <div className={cn('flex items-center gap-2', className)}>
      <Button
        variant="outline"
        size="sm"
        onClick={() => onPageChange(currentPage - 1)}
        disabled={currentPage <= 1}
        className="h-8 w-8 p-0"
      >
        <ChevronLeft className="h-3 w-3" />
      </Button>

      <span className="text-xs text-slate-600 dark:text-slate-400">
        {currentPage}/{totalPages}
      </span>

      <Button
        variant="outline"
        size="sm"
        onClick={() => onPageChange(currentPage + 1)}
        disabled={currentPage >= totalPages}
        className="h-8 w-8 p-0"
      >
        <ChevronRight className="h-3 w-3" />
      </Button>
    </div>
  );
}

/**
 * Page Size Selector Component
 * Allows users to change number of items per page
 * 
 * @example
 * ```tsx
 * <PageSizeSelector
 *   pageSize={pageSize}
 *   onPageSizeChange={(size) => setPageSize(size)}
 * />
 * ```
 */
export function PageSizeSelector({
  pageSize,
  onPageSizeChange,
  options = [10, 20, 50, 100],
  className,
}: {
  pageSize: number;
  onPageSizeChange: (size: number) => void;
  options?: number[];
  className?: string;
}) {
  return (
    <div className={cn('flex items-center gap-2', className)}>
      <span className="text-sm text-slate-600 dark:text-slate-400">Show</span>
      <select
        value={pageSize}
        onChange={(e) => onPageSizeChange(Number(e.target.value))}
        className="h-9 rounded-md border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-900 px-3 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
      >
        {options.map((option) => (
          <option key={option} value={option}>
            {option}
          </option>
        ))}
      </select>
      <span className="text-sm text-slate-600 dark:text-slate-400">per page</span>
    </div>
  );
}
