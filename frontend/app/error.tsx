'use client';

/**
 * Error Boundary for Next.js App Router
 * Catches and displays errors gracefully
 * Feature: 005-view-embedded-docs / Phase 7 - Polish
 */

import { useEffect } from 'react';
import Link from 'next/link';
import { AlertTriangle, RefreshCw, Home } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';

interface ErrorProps {
  error: Error & { digest?: string };
  reset: () => void;
}

/**
 * Error Boundary Component
 * 
 * Displays:
 * - User-friendly error message
 * - Error details (in development)
 * - Reset/retry button
 * - Navigation options
 * 
 * @see https://nextjs.org/docs/app/building-your-application/routing/error-handling
 */
export default function Error({ error, reset }: ErrorProps) {
  useEffect(() => {
    // Log error to console in development
    if (process.env.NODE_ENV === 'development') {
      console.error('Error boundary caught:', error);
    }

    // TODO: Log to error tracking service in production
    // Example: Sentry.captureException(error);
  }, [error]);

  // Check if it's a network error
  const isNetworkError = error.message.includes('fetch') || 
                         error.message.includes('network') ||
                         error.message.includes('Failed to fetch');

  // Check if it's an authentication error
  const isAuthError = error.message.includes('401') || 
                      error.message.includes('unauthorized');

  return (
    <div className="min-h-screen bg-slate-50 dark:bg-slate-950 flex items-center justify-center p-4">
      <Card className="max-w-2xl w-full">
        <CardContent className="p-8">
          {/* Error Icon */}
          <div className="flex justify-center mb-6">
            <div className="p-4 rounded-full bg-red-100 dark:bg-red-900/30">
              <AlertTriangle className="h-12 w-12 text-red-600 dark:text-red-400" />
            </div>
          </div>

          {/* Error Title */}
          <h1 className="text-2xl font-bold text-center text-slate-900 dark:text-slate-100 mb-3">
            {isNetworkError
              ? 'Connection Error'
              : isAuthError
              ? 'Authentication Required'
              : 'Something Went Wrong'}
          </h1>

          {/* Error Message */}
          <p className="text-center text-slate-600 dark:text-slate-400 mb-6">
            {isNetworkError
              ? 'Unable to connect to the server. Please check your internet connection and try again.'
              : isAuthError
              ? 'You need to be logged in to access this page.'
              : 'An unexpected error occurred. We apologize for the inconvenience.'}
          </p>

          {/* Error Details (Development Only) */}
          {process.env.NODE_ENV === 'development' && (
            <details className="mb-6 bg-slate-100 dark:bg-slate-900 rounded-lg p-4">
              <summary className="cursor-pointer text-sm font-semibold text-slate-900 dark:text-slate-100 mb-2">
                Technical Details (Development Only)
              </summary>
              <div className="space-y-2">
                <div>
                  <span className="text-xs font-semibold text-slate-600 dark:text-slate-400">
                    Error Message:
                  </span>
                  <pre className="text-xs text-red-600 dark:text-red-400 mt-1 whitespace-pre-wrap font-mono">
                    {error.message}
                  </pre>
                </div>
                {error.digest && (
                  <div>
                    <span className="text-xs font-semibold text-slate-600 dark:text-slate-400">
                      Error Digest:
                    </span>
                    <pre className="text-xs text-slate-700 dark:text-slate-300 mt-1 font-mono">
                      {error.digest}
                    </pre>
                  </div>
                )}
                {error.stack && (
                  <div>
                    <span className="text-xs font-semibold text-slate-600 dark:text-slate-400">
                      Stack Trace:
                    </span>
                    <pre className="text-xs text-slate-700 dark:text-slate-300 mt-1 whitespace-pre-wrap font-mono max-h-64 overflow-auto">
                      {error.stack}
                    </pre>
                  </div>
                )}
              </div>
            </details>
          )}

          {/* Action Buttons */}
          <div className="flex flex-col sm:flex-row gap-3 justify-center">
            <Button
              onClick={reset}
              size="lg"
              className="gap-2"
            >
              <RefreshCw className="h-5 w-5" />
              Try Again
            </Button>
            <Button
              variant="outline"
              size="lg"
              asChild
              className="gap-2"
            >
              <Link href="/">
                <Home className="h-5 w-5" />
                Go Home
              </Link>
            </Button>
          </div>

          {/* Help Text */}
          <p className="text-center text-sm text-slate-500 dark:text-slate-500 mt-6">
            If the problem persists, please{' '}
            <a
              href="mailto:support@example.com"
              className="text-blue-600 dark:text-blue-400 hover:underline"
            >
              contact support
            </a>
            .
          </p>
        </CardContent>
      </Card>
    </div>
  );
}
