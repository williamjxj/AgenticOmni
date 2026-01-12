/**
 * Auto-Refresh Hook
 * Automatically refresh data for documents in progress
 * Feature: 005-view-embedded-docs / Phase 7 - Polish
 */

import { useEffect, useRef, useCallback } from 'react';

interface UseAutoRefreshOptions {
  /** Enable auto-refresh */
  enabled: boolean;
  /** Refresh interval in milliseconds (default: 5000 = 5 seconds) */
  interval?: number;
  /** Callback function to execute on each refresh */
  onRefresh: () => void | Promise<void>;
  /** Optional condition to check before refreshing */
  condition?: () => boolean;
  /** Maximum number of refreshes (default: unlimited) */
  maxRefreshes?: number;
}

/**
 * Auto-Refresh Hook
 * 
 * Automatically calls a refresh function at regular intervals.
 * Useful for polling documents in processing state.
 * 
 * @example
 * ```tsx
 * useAutoRefresh({
 *   enabled: document.processing_status === 'parsing',
 *   interval: 5000,
 *   onRefresh: () => refetchDocument(),
 * });
 * ```
 */
export function useAutoRefresh({
  enabled,
  interval = 5000,
  onRefresh,
  condition,
  maxRefreshes,
}: UseAutoRefreshOptions) {
  const refreshCountRef = useRef(0);
  const intervalIdRef = useRef<NodeJS.Timeout | null>(null);

  const refresh = useCallback(async () => {
    // Check condition if provided
    if (condition && !condition()) {
      return;
    }

    // Check max refreshes
    if (maxRefreshes && refreshCountRef.current >= maxRefreshes) {
      if (intervalIdRef.current) {
        clearInterval(intervalIdRef.current);
        intervalIdRef.current = null;
      }
      return;
    }

    // Execute refresh
    try {
      await onRefresh();
      refreshCountRef.current += 1;
    } catch (error) {
      console.error('Auto-refresh error:', error);
    }
  }, [onRefresh, condition, maxRefreshes]);

  useEffect(() => {
    if (!enabled) {
      // Clean up existing interval
      if (intervalIdRef.current) {
        clearInterval(intervalIdRef.current);
        intervalIdRef.current = null;
      }
      refreshCountRef.current = 0;
      return;
    }

    // Start auto-refresh
    intervalIdRef.current = setInterval(refresh, interval);

    return () => {
      if (intervalIdRef.current) {
        clearInterval(intervalIdRef.current);
        intervalIdRef.current = null;
      }
    };
  }, [enabled, interval, refresh]);

  return {
    refreshCount: refreshCountRef.current,
    stop: () => {
      if (intervalIdRef.current) {
        clearInterval(intervalIdRef.current);
        intervalIdRef.current = null;
      }
    },
  };
}

/**
 * Auto-Refresh for Processing Documents Hook
 * 
 * Specialized hook for refreshing documents during processing.
 * Automatically stops when document is no longer processing.
 * 
 * @example
 * ```tsx
 * useProcessingAutoRefresh({
 *   documentId: 123,
 *   processingStatus: document.processing_status,
 *   embeddingStatus: document.embedding_status,
 *   onRefresh: () => refetchDocument(),
 * });
 * ```
 */
export function useProcessingAutoRefresh({
  documentId,
  processingStatus,
  embeddingStatus,
  onRefresh,
  interval = 5000,
}: {
  documentId: number;
  processingStatus?: string;
  embeddingStatus?: string;
  onRefresh: () => void | Promise<void>;
  interval?: number;
}) {
  const isProcessing =
    processingStatus === 'parsing' ||
    processingStatus === 'pending' ||
    processingStatus === 'uploaded' ||
    embeddingStatus === 'in_progress';

  return useAutoRefresh({
    enabled: isProcessing,
    interval,
    onRefresh,
    condition: () => isProcessing,
  });
}

/**
 * Auto-Refresh with Exponential Backoff Hook
 * 
 * Increases interval between refreshes using exponential backoff.
 * Useful to reduce server load over time.
 * 
 * @example
 * ```tsx
 * useExponentialBackoffRefresh({
 *   enabled: true,
 *   initialInterval: 2000,
 *   maxInterval: 30000,
 *   onRefresh: () => refetch(),
 * });
 * ```
 */
export function useExponentialBackoffRefresh({
  enabled,
  initialInterval = 2000,
  maxInterval = 30000,
  backoffMultiplier = 1.5,
  onRefresh,
}: {
  enabled: boolean;
  initialInterval?: number;
  maxInterval?: number;
  backoffMultiplier?: number;
  onRefresh: () => void | Promise<void>;
}) {
  const currentIntervalRef = useRef(initialInterval);
  const refreshCountRef = useRef(0);
  const timeoutIdRef = useRef<NodeJS.Timeout | null>(null);

  const scheduleNextRefresh = useCallback(() => {
    if (!enabled) return;

    // Calculate next interval with exponential backoff
    const nextInterval = Math.min(
      currentIntervalRef.current * backoffMultiplier,
      maxInterval
    );
    currentIntervalRef.current = nextInterval;

    timeoutIdRef.current = setTimeout(async () => {
      try {
        await onRefresh();
        refreshCountRef.current += 1;
        scheduleNextRefresh();
      } catch (error) {
        console.error('Exponential backoff refresh error:', error);
        scheduleNextRefresh();
      }
    }, currentIntervalRef.current);
  }, [enabled, backoffMultiplier, maxInterval, onRefresh]);

  useEffect(() => {
    if (!enabled) {
      // Clean up and reset
      if (timeoutIdRef.current) {
        clearTimeout(timeoutIdRef.current);
        timeoutIdRef.current = null;
      }
      currentIntervalRef.current = initialInterval;
      refreshCountRef.current = 0;
      return;
    }

    // Start first refresh
    scheduleNextRefresh();

    return () => {
      if (timeoutIdRef.current) {
        clearTimeout(timeoutIdRef.current);
        timeoutIdRef.current = null;
      }
    };
  }, [enabled, initialInterval, scheduleNextRefresh]);

  return {
    currentInterval: currentIntervalRef.current,
    refreshCount: refreshCountRef.current,
    reset: () => {
      currentIntervalRef.current = initialInterval;
      refreshCountRef.current = 0;
    },
  };
}

/**
 * Visibility-Aware Auto-Refresh Hook
 * 
 * Only refreshes when the page is visible (tab is active).
 * Saves resources when user switches tabs.
 * 
 * @example
 * ```tsx
 * useVisibilityAwareRefresh({
 *   enabled: true,
 *   onRefresh: () => refetch(),
 * });
 * ```
 */
export function useVisibilityAwareRefresh({
  enabled,
  interval = 5000,
  onRefresh,
}: {
  enabled: boolean;
  interval?: number;
  onRefresh: () => void | Promise<void>;
}) {
  const isVisible = usePageVisibility();

  return useAutoRefresh({
    enabled: enabled && isVisible,
    interval,
    onRefresh,
  });
}

/**
 * Page Visibility Hook
 * 
 * Tracks whether the page is currently visible
 * (tab is active, window is not minimized)
 */
function usePageVisibility(): boolean {
  const [isVisible, setIsVisible] = React.useState(
    typeof document !== 'undefined' ? !document.hidden : true
  );

  useEffect(() => {
    const handleVisibilityChange = () => {
      setIsVisible(!document.hidden);
    };

    document.addEventListener('visibilitychange', handleVisibilityChange);

    return () => {
      document.removeEventListener('visibilitychange', handleVisibilityChange);
    };
  }, []);

  return isVisible;
}

// Add React import for usePageVisibility
import React from 'react';
