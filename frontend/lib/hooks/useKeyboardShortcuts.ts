/**
 * Keyboard Shortcuts Hook
 * Global keyboard shortcuts for navigation and actions
 * Feature: 005-view-embedded-docs / Phase 7 - Polish
 */

import { useEffect, useCallback } from 'react';
import { useRouter } from 'next/navigation';

interface KeyboardShortcut {
  key: string;
  ctrlKey?: boolean;
  metaKey?: boolean;
  shiftKey?: boolean;
  altKey?: boolean;
  action: () => void;
  description: string;
}

/**
 * Check if keyboard shortcut matches the event
 */
function matchesShortcut(
  event: KeyboardEvent,
  shortcut: KeyboardShortcut
): boolean {
  if (event.key.toLowerCase() !== shortcut.key.toLowerCase()) return false;
  if (shortcut.ctrlKey && !event.ctrlKey) return false;
  if (shortcut.metaKey && !event.metaKey) return false;
  if (shortcut.shiftKey && !event.shiftKey) return false;
  if (shortcut.altKey && !event.altKey) return false;
  return true;
}

/**
 * Check if we should ignore keyboard events (in input fields, etc.)
 */
function shouldIgnoreEvent(event: KeyboardEvent): boolean {
  const target = event.target as HTMLElement;
  const tagName = target.tagName.toLowerCase();
  
  // Ignore if typing in input, textarea, or contenteditable
  if (tagName === 'input' || tagName === 'textarea') return true;
  if (target.contentEditable === 'true') return true;
  
  return false;
}

/**
 * Keyboard Shortcuts Hook
 * 
 * Registers global keyboard shortcuts for the application.
 * 
 * @example
 * ```tsx
 * function MyComponent() {
 *   useKeyboardShortcuts();
 *   return <div>...</div>;
 * }
 * ```
 */
export function useKeyboardShortcuts() {
  const router = useRouter();

  const shortcuts: KeyboardShortcut[] = [
    // Navigation
    {
      key: '/',
      description: 'Focus search',
      action: () => {
        const searchInput = document.querySelector('input[type="text"]') as HTMLInputElement;
        searchInput?.focus();
      },
    },
    {
      key: 'g',
      shiftKey: true,
      description: 'Go to documents',
      action: () => router.push('/documents'),
    },
    {
      key: 'h',
      shiftKey: true,
      description: 'Go home',
      action: () => router.push('/'),
    },
    {
      key: 'u',
      shiftKey: true,
      description: 'Go to upload',
      action: () => router.push('/upload'),
    },
    {
      key: 's',
      shiftKey: true,
      description: 'Go to search',
      action: () => router.push('/search'),
    },
    // Actions
    {
      key: 'Escape',
      description: 'Close modal / Clear search',
      action: () => {
        // Try to find and trigger close buttons or clear search
        const closeButton = document.querySelector('[data-close-modal]') as HTMLButtonElement;
        if (closeButton) {
          closeButton.click();
        }
      },
    },
    {
      key: 'r',
      ctrlKey: true,
      description: 'Refresh page',
      action: () => window.location.reload(),
    },
    {
      key: '?',
      shiftKey: true,
      description: 'Show keyboard shortcuts',
      action: () => {
        // This will be implemented in a modal later
        console.log('Keyboard shortcuts help');
      },
    },
  ];

  const handleKeyDown = useCallback((event: KeyboardEvent) => {
    // Don't trigger shortcuts when typing in inputs
    if (shouldIgnoreEvent(event)) return;

    // Find matching shortcut
    const matchedShortcut = shortcuts.find((shortcut) =>
      matchesShortcut(event, shortcut)
    );

    if (matchedShortcut) {
      event.preventDefault();
      matchedShortcut.action();
    }
  }, [router]);

  useEffect(() => {
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [handleKeyDown]);

  return shortcuts;
}

/**
 * Hook for component-specific keyboard shortcuts
 * 
 * @example
 * ```tsx
 * useComponentShortcuts({
 *   'Enter': () => handleSubmit(),
 *   'Escape': () => handleClose(),
 * });
 * ```
 */
export function useComponentShortcuts(
  shortcuts: Record<string, () => void>,
  deps: any[] = []
) {
  useEffect(() => {
    const handleKeyDown = (event: KeyboardEvent) => {
      if (shouldIgnoreEvent(event)) return;

      const handler = shortcuts[event.key];
      if (handler) {
        event.preventDefault();
        handler();
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, deps);
}

/**
 * Keyboard Shortcuts Help Component
 * Display available shortcuts in a modal or overlay
 */
export function KeyboardShortcutsHelp() {
  const shortcuts = [
    { keys: ['Shift', 'G'], description: 'Go to documents' },
    { keys: ['Shift', 'H'], description: 'Go home' },
    { keys: ['Shift', 'U'], description: 'Go to upload' },
    { keys: ['Shift', 'S'], description: 'Go to search' },
    { keys: ['/'], description: 'Focus search' },
    { keys: ['Esc'], description: 'Close modal / Clear search' },
    { keys: ['Shift', '?'], description: 'Show this help' },
  ];

  return (
    <div className="space-y-3">
      <h3 className="text-lg font-semibold text-slate-900 dark:text-slate-100">
        Keyboard Shortcuts
      </h3>
      <div className="space-y-2">
        {shortcuts.map((shortcut, index) => (
          <div
            key={index}
            className="flex items-center justify-between py-2 border-b border-slate-200 dark:border-slate-800 last:border-0"
          >
            <span className="text-sm text-slate-700 dark:text-slate-300">
              {shortcut.description}
            </span>
            <div className="flex items-center gap-1">
              {shortcut.keys.map((key, i) => (
                <kbd
                  key={i}
                  className="px-2 py-1 text-xs font-semibold text-slate-900 dark:text-slate-100 bg-slate-100 dark:bg-slate-800 border border-slate-300 dark:border-slate-700 rounded"
                >
                  {key}
                </kbd>
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
