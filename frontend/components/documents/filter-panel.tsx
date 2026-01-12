/**
 * Filter Panel Component
 * Provides filtering and sorting controls for document list
 * Feature: 005-view-embedded-docs / User Story 3
 */

import { Filter, X, ChevronDown, SlidersHorizontal } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import { cn } from '@/lib/utils';
import type { DocumentFilters, SortOptions } from '@/lib/types/document';

interface FilterPanelProps {
  filters: DocumentFilters;
  onFiltersChange: (filters: DocumentFilters) => void;
  sortOptions?: SortOptions;
  onSortChange?: (sort: SortOptions) => void;
  onClearFilters?: () => void;
  className?: string;
  isOpen?: boolean;
  onToggle?: () => void;
}

/**
 * Get filter count (number of active filters)
 */
function getActiveFilterCount(filters: DocumentFilters): number {
  let count = 0;
  if (filters.file_type && filters.file_type.length > 0) count++;
  if (filters.processing_status && filters.processing_status.length > 0) count++;
  if (filters.embedding_status && filters.embedding_status.length > 0) count++;
  if (filters.date_from || filters.date_to) count++;
  if (filters.search_query) count++;
  return count;
}

/**
 * Filter Panel Component
 * 
 * Provides UI for:
 * - File type filtering
 * - Status filtering (processing, embedding)
 * - Date range filtering
 * - Search query
 * - Sorting options
 * - Clear all filters
 * 
 * @example
 * ```tsx
 * <FilterPanel
 *   filters={filters}
 *   onFiltersChange={(newFilters) => setFilters(newFilters)}
 *   sortOptions={sort}
 *   onSortChange={(newSort) => setSort(newSort)}
 * />
 * ```
 */
export function FilterPanel({
  filters,
  onFiltersChange,
  sortOptions,
  onSortChange,
  onClearFilters,
  className,
  isOpen = true,
  onToggle,
}: FilterPanelProps) {
  const activeFilterCount = getActiveFilterCount(filters);
  const hasActiveFilters = activeFilterCount > 0;

  const handleClearAll = () => {
    onFiltersChange({
      page: 1,
      page_size: filters.page_size || 20,
    });
    if (onClearFilters) {
      onClearFilters();
    }
  };

  return (
    <div className={cn('space-y-4', className)}>
      {/* Filter Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Button
            variant="outline"
            size="sm"
            onClick={onToggle}
            className="gap-2"
          >
            <SlidersHorizontal className="h-4 w-4" />
            <span>Filters</span>
            {hasActiveFilters && (
              <span className="ml-1 px-1.5 py-0.5 rounded-full bg-blue-600 text-white text-xs font-medium min-w-[1.25rem] text-center">
                {activeFilterCount}
              </span>
            )}
            <ChevronDown
              className={cn(
                'h-4 w-4 transition-transform',
                isOpen && 'rotate-180'
              )}
            />
          </Button>
        </div>

        {hasActiveFilters && (
          <Button
            variant="ghost"
            size="sm"
            onClick={handleClearAll}
            className="text-slate-600 hover:text-slate-900 dark:text-slate-400 dark:hover:text-slate-100"
          >
            <X className="h-4 w-4 mr-1" />
            Clear All
          </Button>
        )}
      </div>

      {/* Filter Content */}
      {isOpen && (
        <Card>
          <CardContent className="p-6 space-y-6">
            {/* Sort Options */}
            {onSortChange && (
              <div>
                <label className="text-sm font-semibold text-slate-900 dark:text-slate-100 mb-3 block">
                  Sort By
                </label>
                <div className="grid grid-cols-2 gap-3">
                  <select
                    value={sortOptions?.field || 'created_at'}
                    onChange={(e) =>
                      onSortChange({
                        field: e.target.value as SortOptions['field'],
                        order: sortOptions?.order || 'desc',
                      })
                    }
                    className="px-3 py-2 border border-slate-300 dark:border-slate-700 rounded-md bg-white dark:bg-slate-900 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                  >
                    <option value="created_at">Date Created</option>
                    <option value="updated_at">Date Modified</option>
                    <option value="filename">Filename</option>
                    <option value="file_size">File Size</option>
                  </select>

                  <select
                    value={sortOptions?.order || 'desc'}
                    onChange={(e) =>
                      onSortChange({
                        field: sortOptions?.field || 'created_at',
                        order: e.target.value as SortOptions['order'],
                      })
                    }
                    className="px-3 py-2 border border-slate-300 dark:border-slate-700 rounded-md bg-white dark:bg-slate-900 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                  >
                    <option value="desc">Descending</option>
                    <option value="asc">Ascending</option>
                  </select>
                </div>
              </div>
            )}

            {/* File Type Filter */}
            <div>
              <label className="text-sm font-semibold text-slate-900 dark:text-slate-100 mb-3 block">
                File Type
              </label>
              <div className="space-y-2">
                {['pdf', 'docx', 'txt', 'md', 'csv'].map((type) => {
                  const isSelected = filters.file_type?.includes(type) || false;
                  return (
                    <label
                      key={type}
                      className="flex items-center gap-2 cursor-pointer group"
                    >
                      <input
                        type="checkbox"
                        checked={isSelected}
                        onChange={(e) => {
                          const currentTypes = filters.file_type || [];
                          const newTypes = e.target.checked
                            ? [...currentTypes, type]
                            : currentTypes.filter((t) => t !== type);
                          onFiltersChange({
                            ...filters,
                            file_type: newTypes.length > 0 ? newTypes : undefined,
                            page: 1,
                          });
                        }}
                        className="w-4 h-4 rounded border-slate-300 dark:border-slate-700 text-blue-600 focus:ring-2 focus:ring-blue-500"
                      />
                      <span className="text-sm text-slate-700 dark:text-slate-300 group-hover:text-slate-900 dark:group-hover:text-slate-100">
                        {type.toUpperCase()}
                      </span>
                    </label>
                  );
                })}
              </div>
            </div>

            {/* Processing Status Filter */}
            <div>
              <label className="text-sm font-semibold text-slate-900 dark:text-slate-100 mb-3 block">
                Processing Status
              </label>
              <div className="space-y-2">
                {[
                  { value: 'uploaded', label: 'Uploaded' },
                  { value: 'pending', label: 'Pending' },
                  { value: 'parsing', label: 'Processing' },
                  { value: 'parsed', label: 'Ready' },
                  { value: 'failed', label: 'Failed' },
                ].map((status) => {
                  const isSelected =
                    filters.processing_status?.includes(status.value as any) || false;
                  return (
                    <label
                      key={status.value}
                      className="flex items-center gap-2 cursor-pointer group"
                    >
                      <input
                        type="checkbox"
                        checked={isSelected}
                        onChange={(e) => {
                          const currentStatuses = filters.processing_status || [];
                          const newStatuses = e.target.checked
                            ? [...currentStatuses, status.value as any]
                            : currentStatuses.filter((s) => s !== status.value);
                          onFiltersChange({
                            ...filters,
                            processing_status:
                              newStatuses.length > 0 ? newStatuses : undefined,
                            page: 1,
                          });
                        }}
                        className="w-4 h-4 rounded border-slate-300 dark:border-slate-700 text-blue-600 focus:ring-2 focus:ring-blue-500"
                      />
                      <span className="text-sm text-slate-700 dark:text-slate-300 group-hover:text-slate-900 dark:group-hover:text-slate-100">
                        {status.label}
                      </span>
                    </label>
                  );
                })}
              </div>
            </div>

            {/* Embedding Status Filter */}
            <div>
              <label className="text-sm font-semibold text-slate-900 dark:text-slate-100 mb-3 block">
                Embedding Status
              </label>
              <div className="space-y-2">
                {[
                  { value: 'not_started', label: 'Not Started' },
                  { value: 'in_progress', label: 'In Progress' },
                  { value: 'completed', label: 'Completed' },
                  { value: 'failed', label: 'Failed' },
                ].map((status) => {
                  const isSelected =
                    filters.embedding_status?.includes(status.value as any) || false;
                  return (
                    <label
                      key={status.value}
                      className="flex items-center gap-2 cursor-pointer group"
                    >
                      <input
                        type="checkbox"
                        checked={isSelected}
                        onChange={(e) => {
                          const currentStatuses = filters.embedding_status || [];
                          const newStatuses = e.target.checked
                            ? [...currentStatuses, status.value as any]
                            : currentStatuses.filter((s) => s !== status.value);
                          onFiltersChange({
                            ...filters,
                            embedding_status:
                              newStatuses.length > 0 ? newStatuses : undefined,
                            page: 1,
                          });
                        }}
                        className="w-4 h-4 rounded border-slate-300 dark:border-slate-700 text-blue-600 focus:ring-2 focus:ring-blue-500"
                      />
                      <span className="text-sm text-slate-700 dark:text-slate-300 group-hover:text-slate-900 dark:group-hover:text-slate-100">
                        {status.label}
                      </span>
                    </label>
                  );
                })}
              </div>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}

/**
 * Active Filters Display
 * Shows currently active filters as removable chips
 */
export function ActiveFilters({
  filters,
  onRemoveFilter,
  className,
}: {
  filters: DocumentFilters;
  onRemoveFilter: (filterKey: keyof DocumentFilters, value?: string) => void;
  className?: string;
}) {
  const activeFilters: Array<{
    key: keyof DocumentFilters;
    label: string;
    value?: string;
  }> = [];

  // File types
  filters.file_type?.forEach((type) => {
    activeFilters.push({
      key: 'file_type',
      label: `Type: ${type.toUpperCase()}`,
      value: type,
    });
  });

  // Processing statuses
  filters.processing_status?.forEach((status) => {
    activeFilters.push({
      key: 'processing_status',
      label: `Status: ${status}`,
      value: status,
    });
  });

  // Embedding statuses
  filters.embedding_status?.forEach((status) => {
    activeFilters.push({
      key: 'embedding_status',
      label: `Embedding: ${status}`,
      value: status,
    });
  });

  // Date range
  if (filters.date_from || filters.date_to) {
    activeFilters.push({
      key: 'date_from',
      label: `Date: ${filters.date_from || '...'} to ${filters.date_to || '...'}`,
    });
  }

  // Search query
  if (filters.search_query) {
    activeFilters.push({
      key: 'search_query',
      label: `Search: "${filters.search_query}"`,
    });
  }

  if (activeFilters.length === 0) return null;

  return (
    <div className={cn('flex flex-wrap gap-2', className)}>
      {activeFilters.map((filter, index) => (
        <button
          key={`${filter.key}-${filter.value || index}`}
          onClick={() => onRemoveFilter(filter.key, filter.value)}
          className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-blue-100 dark:bg-blue-900/30 text-blue-800 dark:text-blue-200 text-sm hover:bg-blue-200 dark:hover:bg-blue-900/50 transition-colors"
        >
          <span>{filter.label}</span>
          <X className="h-3 w-3" />
        </button>
      ))}
    </div>
  );
}
