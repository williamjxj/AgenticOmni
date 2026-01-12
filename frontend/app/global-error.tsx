'use client';

/**
 * Global Error Boundary for Next.js App Router
 * Catches errors in the root layout
 * Feature: 005-view-embedded-docs / Phase 7 - Polish
 */

import { useEffect } from 'react';

interface GlobalErrorProps {
  error: Error & { digest?: string };
  reset: () => void;
}

/**
 * Global Error Boundary
 * 
 * This catches errors that occur in the root layout.
 * Must be defined separately from the regular error.tsx.
 * 
 * @see https://nextjs.org/docs/app/building-your-application/routing/error-handling#handling-errors-in-root-layouts
 */
export default function GlobalError({ error, reset }: GlobalErrorProps) {
  useEffect(() => {
    // Log error to console
    console.error('Global error boundary caught:', error);

    // TODO: Log to error tracking service
    // Example: Sentry.captureException(error);
  }, [error]);

  return (
    <html>
      <body>
        <div style={{
          minHeight: '100vh',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          padding: '1rem',
          backgroundColor: '#f8fafc',
        }}>
          <div style={{
            maxWidth: '32rem',
            width: '100%',
            backgroundColor: 'white',
            borderRadius: '0.5rem',
            boxShadow: '0 4px 6px rgba(0, 0, 0, 0.1)',
            padding: '2rem',
            textAlign: 'center',
          }}>
            <div style={{
              fontSize: '3rem',
              marginBottom: '1rem',
            }}>
              ⚠️
            </div>
            <h1 style={{
              fontSize: '1.5rem',
              fontWeight: 'bold',
              color: '#1e293b',
              marginBottom: '0.5rem',
            }}>
              Application Error
            </h1>
            <p style={{
              color: '#64748b',
              marginBottom: '1.5rem',
            }}>
              A critical error occurred. Please refresh the page or contact support if the problem persists.
            </p>
            <button
              onClick={reset}
              style={{
                backgroundColor: '#3b82f6',
                color: 'white',
                padding: '0.75rem 1.5rem',
                borderRadius: '0.375rem',
                border: 'none',
                cursor: 'pointer',
                fontSize: '1rem',
                fontWeight: '500',
              }}
            >
              Try Again
            </button>
            {process.env.NODE_ENV === 'development' && (
              <details style={{
                marginTop: '1.5rem',
                textAlign: 'left',
                backgroundColor: '#f1f5f9',
                padding: '1rem',
                borderRadius: '0.375rem',
              }}>
                <summary style={{ cursor: 'pointer', fontWeight: '600', marginBottom: '0.5rem' }}>
                  Error Details
                </summary>
                <pre style={{
                  fontSize: '0.75rem',
                  color: '#dc2626',
                  whiteSpace: 'pre-wrap',
                  wordBreak: 'break-word',
                }}>
                  {error.message}
                </pre>
              </details>
            )}
          </div>
        </div>
      </body>
    </html>
  );
}
