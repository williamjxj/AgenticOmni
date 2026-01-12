/**
 * React hooks for document state management
 * Feature: 005-view-embedded-docs
 */

import { useCallback, useEffect, useState } from 'react';
import {
  Document,
  DocumentDetailResponse,
  DocumentFilters,
  DocumentListResponse,
  ApiError,
  SortOptions,
} from '@/lib/types/document';
import {
  fetchDocuments,
  fetchDocumentById,
} from '@/lib/api/documents';

// ============================================================================
// Types
// ============================================================================

interface UseDocumentsState {
  documents: Document[];
  total: number;
  page: number;
  totalPages: number;
  loading: boolean;
  error: ApiError | null;
}

interface UseDocumentsActions {
  refetch: () => Promise<void>;
  setPage: (page: number) => void;
  setFilters: (filters: DocumentFilters) => void;
  setSort: (sort: SortOptions | undefined) => void;
}

interface UseDocumentDetailState {
  document: DocumentDetailResponse | null;
  loading: boolean;
  error: ApiError | null;
}

interface UseDocumentDetailActions {
  refetch: () => Promise<void>;
}

// ============================================================================
// useDocuments Hook - List Management
// ============================================================================

/**
 * Hook for managing document list state with pagination and filtering
 * 
 * @example
 * ```tsx
 * const { documents, loading, error, refetch, setPage } = useDocuments({
 *   page: 1,
 *   filters: { processing_status: ['parsed'] }
 * });
 * ```
 */
export function useDocuments(
  initialFilters: DocumentFilters = { page: 1, page_size: 20 },
  initialSort?: SortOptions
): UseDocumentsState & UseDocumentsActions {
  const [state, setState] = useState<UseDocumentsState>({
    documents: [],
    total: 0,
    page: initialFilters.page || 1,
    totalPages: 1,
    loading: true,
    error: null,
  });

  const [filters, setFilters] = useState<DocumentFilters>(initialFilters);
  const [sort, setSort] = useState<SortOptions | undefined>(initialSort);

  const fetchData = useCallback(async () => {
    setState((prev) => ({ ...prev, loading: true, error: null }));

    try {
      const response = await fetchDocuments(filters, sort);
      
      setState({
        documents: response.documents,
        total: response.total,
        page: response.page,
        totalPages: response.total_pages,
        loading: false,
        error: null,
      });
    } catch (err) {
      const apiError = err instanceof ApiError ? err : new ApiError(
        500,
        'unknown',
        err instanceof Error ? err.message : 'An unexpected error occurred'
      );
      
      setState((prev) => ({
        ...prev,
        loading: false,
        error: apiError,
      }));
    }
  }, [filters, sort]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  const setPage = useCallback((page: number) => {
    setFilters((prev) => ({ ...prev, page }));
  }, []);

  const updateFilters = useCallback((newFilters: DocumentFilters) => {
    setFilters((prev) => ({ ...prev, ...newFilters, page: 1 }));
  }, []);

  return {
    ...state,
    refetch: fetchData,
    setPage,
    setFilters: updateFilters,
    setSort,
  };
}

// ============================================================================
// useDocumentDetail Hook - Single Document
// ============================================================================

/**
 * Hook for managing single document detail state
 * 
 * @example
 * ```tsx
 * const { document, loading, error, refetch } = useDocumentDetail(123);
 * ```
 */
export function useDocumentDetail(
  documentId: number,
  includeChunks: boolean = false
): UseDocumentDetailState & UseDocumentDetailActions {
  const [state, setState] = useState<UseDocumentDetailState>({
    document: null,
    loading: true,
    error: null,
  });

  const fetchData = useCallback(async () => {
    if (!documentId) return;

    setState((prev) => ({ ...prev, loading: true, error: null }));

    try {
      const document = await fetchDocumentById(documentId, includeChunks);
      
      setState({
        document,
        loading: false,
        error: null,
      });
    } catch (err) {
      const apiError = err instanceof ApiError ? err : new ApiError(
        500,
        'unknown',
        err instanceof Error ? err.message : 'An unexpected error occurred'
      );
      
      setState({
        document: null,
        loading: false,
        error: apiError,
      });
    }
  }, [documentId, includeChunks]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  return {
    ...state,
    refetch: fetchData,
  };
}

// ============================================================================
// useDocumentPolling Hook - Auto-refresh for In-Progress Documents
// ============================================================================

/**
 * Hook that polls document status for in-progress documents
 * Useful for showing real-time updates during processing
 * 
 * @example
 * ```tsx
 * useDocumentPolling(documentId, {
 *   enabled: document?.processing_status === 'parsing',
 *   interval: 3000,
 *   onComplete: () => toast.success('Document ready!')
 * });
 * ```
 */
export function useDocumentPolling(
  documentId: number,
  options: {
    enabled: boolean;
    interval?: number;
    onComplete?: (document: DocumentDetailResponse) => void;
    onError?: (error: ApiError) => void;
  }
) {
  const { enabled, interval = 3000, onComplete, onError } = options;
  const [pollingCount, setPollingCount] = useState(0);

  useEffect(() => {
    if (!enabled || !documentId) return;

    const poll = async () => {
      try {
        const document = await fetchDocumentById(documentId);
        
        // Stop polling if document is no longer processing
        const isProcessing = 
          document.processing_status === 'parsing' ||
          document.processing_status === 'pending' ||
          document.embedding_status === 'in_progress';

        if (!isProcessing && onComplete) {
          onComplete(document);
        }

        setPollingCount((c) => c + 1);
      } catch (err) {
        if (onError && err instanceof ApiError) {
          onError(err);
        }
      }
    };

    const intervalId = setInterval(poll, interval);
    return () => clearInterval(intervalId);
  }, [documentId, enabled, interval, onComplete, onError]);

  return { pollingCount };
}

// ============================================================================
// useLocalStorage Hook - Persist Filters
// ============================================================================

/**
 * Hook to persist document filters in localStorage
 */
export function usePersistedFilters(
  key: string = 'document-filters',
  initialFilters: DocumentFilters = { page: 1, page_size: 20 }
): [DocumentFilters, (filters: DocumentFilters) => void] {
  const [filters, setFiltersState] = useState<DocumentFilters>(() => {
    if (typeof window === 'undefined') return initialFilters;
    
    try {
      const saved = localStorage.getItem(key);
      return saved ? JSON.parse(saved) : initialFilters;
    } catch {
      return initialFilters;
    }
  });

  const setFilters = useCallback((newFilters: DocumentFilters) => {
    setFiltersState(newFilters);
    if (typeof window !== 'undefined') {
      localStorage.setItem(key, JSON.stringify(newFilters));
    }
  }, [key]);

  return [filters, setFilters];
}
