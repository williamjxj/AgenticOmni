'use client';

/**
 * Documents List Page with Filtering & Search
 * Feature: 005-view-embedded-docs / User Stories 1 & 3
 * Displays a filterable, searchable, paginated list of documents
 */

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { ArrowLeft, RefreshCw, Upload, Search as SearchIcon, CheckCircle2, Sparkles } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import { useDocuments } from '@/lib/hooks/useDocuments';
import { DocumentList } from '@/components/documents/document-list';
import { Pagination } from '@/components/documents/pagination';
import { FilterPanel, ActiveFilters } from '@/components/documents/filter-panel';
import { SearchInput } from '@/components/documents/search-input';
import { DateRangePicker } from '@/components/documents/date-range-picker';
import { getErrorMessage } from '@/lib/utils/error-handling';
import type { DocumentFilters, SortOptions } from '@/lib/types/document';

/**
 * Documents Page Component with Filtering & Search
 * 
 * Provides:
 * - Paginated document list
 * - Search by filename/content
 * - Filter by file type, status, embedding status
 * - Date range filtering
 * - Sorting options
 * - Active filters display
 * - Loading states with skeletons
 * - Empty state handling
 * - Responsive layout
 */
export default function DocumentsPage() {
  const router = useRouter();
  const [isFilterOpen, setIsFilterOpen] = useState(false);
  
  // Use the documents hook for state management with filters
  const {
    documents,
    total,
    page,
    totalPages,
    loading,
    error,
    refetch,
    setPage,
    setFilters: updateFilters,
    setSort,
  } = useDocuments({
    page: 1,
    page_size: 20,
  });

  // Get current filters from hook (would need to be exposed)
  // For now, we'll manage filters locally
  const [localFilters, setLocalFilters] = useState<DocumentFilters>({
    page: 1,
    page_size: 20,
  });
  
  const [sortOptions, setSortOptions] = useState<SortOptions>({
    field: 'created_at',
    order: 'desc',
  });

  // Check if any documents are ready for search
  const hasSearchableDocuments = documents.some(
    (doc) => doc.processing_status === 'parsed' && doc.embedding_status === 'completed'
  );

  const handleDocumentClick = (documentId: number) => {
    router.push(`/documents/${documentId}`);
  };

  const handleDocumentDownload = async (documentId: number) => {
    // TODO: Implement download functionality
    console.log('Download document:', documentId);
  };

  const handleFiltersChange = (newFilters: DocumentFilters) => {
    setLocalFilters(newFilters);
    updateFilters(newFilters);
  };

  const handleSortChange = (newSort: SortOptions) => {
    setSortOptions(newSort);
    setSort(newSort);
  };

  const handleSearchChange = (query: string) => {
    handleFiltersChange({
      ...localFilters,
      search_query: query || undefined,
      page: 1,
    });
  };

  const handleRemoveFilter = (filterKey: keyof DocumentFilters, value?: string) => {
    const newFilters = { ...localFilters };

    if (filterKey === 'file_type' && value) {
      newFilters.file_type = newFilters.file_type?.filter((t) => t !== value);
      if (newFilters.file_type?.length === 0) delete newFilters.file_type;
    } else if (filterKey === 'processing_status' && value) {
      newFilters.processing_status = newFilters.processing_status?.filter(
        (s) => s !== value
      );
      if (newFilters.processing_status?.length === 0)
        delete newFilters.processing_status;
    } else if (filterKey === 'embedding_status' && value) {
      newFilters.embedding_status = newFilters.embedding_status?.filter(
        (s) => s !== value
      );
      if (newFilters.embedding_status?.length === 0)
        delete newFilters.embedding_status;
    } else if (filterKey === 'date_from') {
      delete newFilters.date_from;
      delete newFilters.date_to;
    } else if (filterKey === 'search_query') {
      delete newFilters.search_query;
    }

    newFilters.page = 1;
    handleFiltersChange(newFilters);
  };

  const handleClearAllFilters = () => {
    const resetFilters: DocumentFilters = {
      page: 1,
      page_size: localFilters.page_size || 20,
    };
    setLocalFilters(resetFilters);
    updateFilters(resetFilters);
  };

  return (
    <div className="min-h-screen bg-slate-50 dark:bg-slate-950">
      {/* Header */}
      <header className="sticky top-0 z-10 border-b bg-white dark:bg-slate-900 shadow-sm">
        <div className="container mx-auto px-4 py-4">
          <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
            {/* Title section */}
            <div className="flex items-center gap-4">
              <Button variant="ghost" size="sm" asChild className="hidden sm:inline-flex">
                <Link href="/">
                  <ArrowLeft className="h-4 w-4 mr-2" />
                  Back
                </Link>
              </Button>
              <div>
                <h1 className="text-2xl font-bold text-slate-900 dark:text-slate-100">
                  My Documents
                </h1>
                {!loading && total > 0 && (
                  <p className="text-sm text-slate-600 dark:text-slate-400 mt-1">
                    {total} {total === 1 ? 'document' : 'documents'} total
                  </p>
                )}
              </div>
            </div>

            {/* Action buttons */}
            <div className="flex gap-2 w-full sm:w-auto">
              <Button
                variant="outline"
                size="sm"
                onClick={refetch}
                disabled={loading}
                className="flex-1 sm:flex-none"
              >
                <RefreshCw className={`h-4 w-4 mr-2 ${loading ? 'animate-spin' : ''}`} />
                Refresh
              </Button>
              <Button asChild className="flex-1 sm:flex-none">
                <Link href="/upload">
                  <Upload className="h-4 w-4 mr-2" />
                  Upload
                </Link>
              </Button>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="container mx-auto px-4 py-6 sm:py-8">
        <div className="max-w-6xl mx-auto space-y-6">
          {/* Ready for Search Card */}
          {!loading && hasSearchableDocuments && (
            <Card className="bg-linear-to-r from-blue-50 to-purple-50 dark:from-blue-950 dark:to-purple-950 border-2 border-blue-200 dark:border-blue-800">
              <CardContent className="p-6">
                <div className="flex flex-col sm:flex-row items-start sm:items-center gap-4">
                  <div className="shrink-0">
                    <CheckCircle2 className="h-10 w-10 text-green-600" />
                  </div>
                  <div className="flex-1 space-y-2">
                    <h3 className="text-lg font-semibold flex items-center gap-2">
                      <Sparkles className="h-5 w-5 text-purple-600" />
                      Your Documents Are Ready!
                    </h3>
                    <p className="text-slate-700 dark:text-slate-300">
                      Your documents have been processed and embedded. Start searching through them using natural language queries.
                    </p>
                  </div>
                  <Button size="lg" asChild className="w-full sm:w-auto">
                    <Link href="/search">
                      <SearchIcon className="mr-2 h-5 w-5" />
                      Start Searching
                    </Link>
                  </Button>
                </div>
              </CardContent>
            </Card>
          )}

          {/* Search Bar */}
          <SearchInput
            value={localFilters.search_query || ''}
            onChange={handleSearchChange}
            placeholder="Search documents by name or content..."
            loading={loading}
          />

          {/* Active Filters */}
          <ActiveFilters
            filters={localFilters}
            onRemoveFilter={handleRemoveFilter}
          />

          {/* Filter Panel */}
          <FilterPanel
            filters={localFilters}
            onFiltersChange={handleFiltersChange}
            sortOptions={sortOptions}
            onSortChange={handleSortChange}
            onClearFilters={handleClearAllFilters}
            isOpen={isFilterOpen}
            onToggle={() => setIsFilterOpen(!isFilterOpen)}
          />

          {/* Date Range Picker (within filter panel if expanded) */}
          {isFilterOpen && (
            <Card>
              <CardContent className="p-6">
                <DateRangePicker
                  startDate={localFilters.date_from}
                  endDate={localFilters.date_to}
                  onRangeChange={(start, end) => {
                    handleFiltersChange({
                      ...localFilters,
                      date_from: start,
                      date_to: end,
                      page: 1,
                    });
                  }}
                />
              </CardContent>
            </Card>
          )}

          {/* Document List */}
          <DocumentList
            documents={documents}
            loading={loading}
            error={error ? getErrorMessage(error) : null}
            emptyVariant={
              localFilters.search_query || 
              localFilters.file_type?.length ||
              localFilters.processing_status?.length ||
              localFilters.embedding_status?.length ||
              localFilters.date_from ||
              localFilters.date_to
                ? 'no-filtered-results'
                : 'no-documents'
            }
            onDocumentClick={handleDocumentClick}
            onDocumentDownload={handleDocumentDownload}
            onRetry={refetch}
          />

          {/* Pagination */}
          {!loading && totalPages > 1 && (
            <Pagination
              currentPage={page}
              totalPages={totalPages}
              totalItems={total}
              pageSize={20}
              onPageChange={setPage}
              showFirstLast={totalPages > 5}
              showPageInfo={true}
            />
          )}
        </div>
      </main>
    </div>
  );
}
