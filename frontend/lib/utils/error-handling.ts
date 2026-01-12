/**
 * Error handling utilities for the frontend
 * Feature: 005-view-embedded-docs
 */

import { ApiError, DocumentError } from '@/lib/types/document';

// ============================================================================
// Error Type Guards
// ============================================================================

/**
 * Check if error is an ApiError
 */
export function isApiError(error: unknown): error is ApiError {
  return error instanceof ApiError;
}

/**
 * Check if error is a DocumentError
 */
export function isDocumentError(error: unknown): error is DocumentError {
  return error instanceof DocumentError;
}

/**
 * Check if error is a network error
 */
export function isNetworkError(error: unknown): boolean {
  if (error instanceof TypeError && error.message.includes('fetch')) {
    return true;
  }
  if (isApiError(error) && error.statusCode === 0) {
    return true;
  }
  return false;
}

// ============================================================================
// Error Message Formatting
// ============================================================================

/**
 * Get user-friendly error message from any error type
 */
export function getErrorMessage(error: unknown): string {
  if (isApiError(error)) {
    return formatApiError(error);
  }
  
  if (isDocumentError(error)) {
    return error.message;
  }

  if (error instanceof Error) {
    return error.message;
  }

  return 'An unexpected error occurred. Please try again.';
}

/**
 * Format API error with context-specific messages
 */
export function formatApiError(error: ApiError): string {
  // Network errors
  if (isNetworkError(error)) {
    return 'Unable to connect to the server. Please check your internet connection.';
  }

  // HTTP status-based messages
  switch (error.statusCode) {
    case 400:
      return error.message || 'Invalid request. Please check your input.';
    case 401:
      return 'You are not authorized. Please log in again.';
    case 403:
      return 'You do not have permission to perform this action.';
    case 404:
      return 'The requested resource was not found.';
    case 409:
      return error.message || 'A conflict occurred. The resource may already exist.';
    case 413:
      return 'The file is too large to upload.';
    case 422:
      return error.message || 'Validation failed. Please check your input.';
    case 429:
      return 'Too many requests. Please wait a moment and try again.';
    case 500:
      return 'A server error occurred. Please try again later.';
    case 502:
    case 503:
    case 504:
      return 'The server is temporarily unavailable. Please try again later.';
    default:
      return error.message || 'An unexpected error occurred.';
  }
}

/**
 * Get error title for display in alerts/toasts
 */
export function getErrorTitle(error: unknown): string {
  if (isApiError(error)) {
    if (isNetworkError(error)) return 'Connection Error';
    if (error.statusCode >= 500) return 'Server Error';
    if (error.statusCode === 404) return 'Not Found';
    if (error.statusCode === 403) return 'Permission Denied';
    if (error.statusCode === 401) return 'Unauthorized';
    return 'Request Failed';
  }

  if (isDocumentError(error)) {
    return 'Document Error';
  }

  return 'Error';
}

// ============================================================================
// Error Action Suggestions
// ============================================================================

/**
 * Get actionable suggestions based on error type
 */
export function getErrorSuggestions(error: unknown): string[] {
  if (isNetworkError(error)) {
    return [
      'Check your internet connection',
      'Verify the backend server is running',
      'Try refreshing the page',
    ];
  }

  if (isApiError(error)) {
    switch (error.statusCode) {
      case 400:
      case 422:
        return [
          'Review your input for errors',
          'Check that all required fields are filled',
        ];
      case 401:
        return [
          'Log in again',
          'Check your credentials',
        ];
      case 403:
        return [
          'Contact your administrator for access',
          'Verify you have the correct permissions',
        ];
      case 404:
        return [
          'Verify the URL is correct',
          'Check that the document exists',
          'Return to the documents list',
        ];
      case 413:
        return [
          'Try uploading a smaller file',
          'Compress the file before uploading',
        ];
      case 429:
        return [
          'Wait a few moments before trying again',
          'Reduce the frequency of requests',
        ];
      case 500:
      case 502:
      case 503:
      case 504:
        return [
          'Wait a few minutes and try again',
          'Check the server status',
          'Contact support if the problem persists',
        ];
    }
  }

  return ['Try again', 'Contact support if the problem persists'];
}

// ============================================================================
// Error Logging
// ============================================================================

/**
 * Log error with context for debugging
 */
export function logError(
  error: unknown,
  context: {
    component?: string;
    action?: string;
    metadata?: Record<string, any>;
  } = {}
): void {
  const errorInfo = {
    timestamp: new Date().toISOString(),
    error: {
      name: error instanceof Error ? error.name : 'Unknown',
      message: getErrorMessage(error),
      stack: error instanceof Error ? error.stack : undefined,
    },
    context,
  };

  // Log to console in development
  if (process.env.NODE_ENV === 'development') {
    console.error('Error occurred:', errorInfo);
  }

  // In production, you could send to an error tracking service
  // e.g., Sentry, LogRocket, etc.
  if (process.env.NODE_ENV === 'production') {
    // TODO: Integrate with error tracking service
    // Example: Sentry.captureException(error, { contexts: { custom: context } });
  }
}

// ============================================================================
// Retry Logic
// ============================================================================

/**
 * Check if error is retryable
 */
export function isRetryableError(error: unknown): boolean {
  if (isNetworkError(error)) return true;

  if (isApiError(error)) {
    // Retry on server errors and rate limiting
    return error.statusCode >= 500 || error.statusCode === 429;
  }

  return false;
}

/**
 * Get retry delay in milliseconds based on attempt number
 * Uses exponential backoff: 1s, 2s, 4s, 8s, 16s
 */
export function getRetryDelay(attempt: number): number {
  const baseDelay = 1000; // 1 second
  const maxDelay = 16000; // 16 seconds
  const delay = baseDelay * Math.pow(2, attempt - 1);
  return Math.min(delay, maxDelay);
}

/**
 * Retry a function with exponential backoff
 * 
 * @example
 * ```ts
 * const result = await retryWithBackoff(
 *   () => fetchDocuments(),
 *   { maxRetries: 3, onRetry: (attempt) => console.log(`Retry ${attempt}`) }
 * );
 * ```
 */
export async function retryWithBackoff<T>(
  fn: () => Promise<T>,
  options: {
    maxRetries?: number;
    onRetry?: (attempt: number, error: unknown) => void;
    shouldRetry?: (error: unknown) => boolean;
  } = {}
): Promise<T> {
  const {
    maxRetries = 3,
    onRetry,
    shouldRetry = isRetryableError,
  } = options;

  let lastError: unknown;

  for (let attempt = 1; attempt <= maxRetries + 1; attempt++) {
    try {
      return await fn();
    } catch (error) {
      lastError = error;

      // Don't retry if this is the last attempt
      if (attempt > maxRetries) break;

      // Don't retry if error is not retryable
      if (!shouldRetry(error)) break;

      // Call onRetry callback
      if (onRetry) onRetry(attempt, error);

      // Wait before retrying
      await new Promise((resolve) =>
        setTimeout(resolve, getRetryDelay(attempt))
      );
    }
  }

  throw lastError;
}

// ============================================================================
// Error Boundary Helpers
// ============================================================================

/**
 * Check if error should trigger error boundary fallback
 */
export function isCriticalError(error: unknown): boolean {
  if (isApiError(error)) {
    // 401/403 should redirect to login, not show error boundary
    if (error.statusCode === 401 || error.statusCode === 403) {
      return false;
    }
    // 404 should show "not found" page, not error boundary
    if (error.statusCode === 404) {
      return false;
    }
    // Server errors are critical
    return error.statusCode >= 500;
  }

  // Unknown errors are critical
  return true;
}

/**
 * Format error for display in error boundary
 */
export function formatErrorForBoundary(error: unknown): {
  title: string;
  message: string;
  suggestions: string[];
  technical?: string;
} {
  return {
    title: getErrorTitle(error),
    message: getErrorMessage(error),
    suggestions: getErrorSuggestions(error),
    technical:
      process.env.NODE_ENV === 'development' && error instanceof Error
        ? error.stack
        : undefined,
  };
}
