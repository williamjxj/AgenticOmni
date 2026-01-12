/**
 * Accessibility Utilities
 * Helper functions for improving accessibility (ARIA, focus management, etc.)
 * Feature: 005-view-embedded-docs / Phase 7 - Polish
 */

/**
 * Announce message to screen readers
 * Uses ARIA live regions to announce dynamic content changes
 * 
 * @example
 * ```ts
 * announceToScreenReader('Document uploaded successfully');
 * ```
 */
export function announceToScreenReader(
  message: string,
  priority: 'polite' | 'assertive' = 'polite'
): void {
  const announcement = document.createElement('div');
  announcement.setAttribute('role', 'status');
  announcement.setAttribute('aria-live', priority);
  announcement.setAttribute('aria-atomic', 'true');
  announcement.className = 'sr-only'; // Screen reader only
  announcement.style.position = 'absolute';
  announcement.style.left = '-10000px';
  announcement.style.width = '1px';
  announcement.style.height = '1px';
  announcement.style.overflow = 'hidden';
  
  document.body.appendChild(announcement);
  
  // Set message after a brief delay to ensure screen readers pick it up
  setTimeout(() => {
    announcement.textContent = message;
  }, 100);
  
  // Remove after announcement
  setTimeout(() => {
    document.body.removeChild(announcement);
  }, 1000);
}

/**
 * Trap focus within a container (for modals, dialogs)
 * 
 * @example
 * ```tsx
 * useEffect(() => {
 *   const cleanup = trapFocus(modalRef.current);
 *   return cleanup;
 * }, []);
 * ```
 */
export function trapFocus(element: HTMLElement | null): () => void {
  if (!element) return () => {};

  const focusableElements = element.querySelectorAll<HTMLElement>(
    'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
  );

  const firstFocusable = focusableElements[0];
  const lastFocusable = focusableElements[focusableElements.length - 1];

  // Focus first element
  firstFocusable?.focus();

  const handleKeyDown = (e: KeyboardEvent) => {
    if (e.key !== 'Tab') return;

    if (e.shiftKey) {
      // Shift + Tab
      if (document.activeElement === firstFocusable) {
        e.preventDefault();
        lastFocusable?.focus();
      }
    } else {
      // Tab
      if (document.activeElement === lastFocusable) {
        e.preventDefault();
        firstFocusable?.focus();
      }
    }
  };

  element.addEventListener('keydown', handleKeyDown);

  return () => {
    element.removeEventListener('keydown', handleKeyDown);
  };
}

/**
 * Restore focus to a previous element
 * Useful when closing modals to return focus to trigger button
 * 
 * @example
 * ```tsx
 * const previousFocus = document.activeElement as HTMLElement;
 * // ... open modal ...
 * restoreFocus(previousFocus);
 * ```
 */
export function restoreFocus(element: HTMLElement | null): void {
  if (element && typeof element.focus === 'function') {
    element.focus();
  }
}

/**
 * Get ARIA label for file type
 */
export function getFileTypeAriaLabel(fileType: string): string {
  const labels: Record<string, string> = {
    pdf: 'PDF document',
    docx: 'Word document',
    doc: 'Word document',
    txt: 'Text file',
    md: 'Markdown file',
    csv: 'CSV spreadsheet',
    xlsx: 'Excel spreadsheet',
    xls: 'Excel spreadsheet',
  };
  
  return labels[fileType.toLowerCase()] || `${fileType} file`;
}

/**
 * Get ARIA label for processing status
 */
export function getProcessingStatusAriaLabel(status: string): string {
  const labels: Record<string, string> = {
    uploaded: 'Status: Uploaded, awaiting processing',
    pending: 'Status: Pending, queued for processing',
    parsing: 'Status: Processing, document is being parsed',
    parsed: 'Status: Ready, document is processed and searchable',
    failed: 'Status: Failed, processing encountered an error',
  };
  
  return labels[status] || `Status: ${status}`;
}

/**
 * Get ARIA label for embedding status
 */
export function getEmbeddingStatusAriaLabel(status: string): string {
  const labels: Record<string, string> = {
    not_started: 'Embedding status: Not started',
    in_progress: 'Embedding status: In progress, generating vector embeddings',
    completed: 'Embedding status: Completed, document is embedded and searchable',
    failed: 'Embedding status: Failed, embedding generation encountered an error',
  };
  
  return labels[status] || `Embedding status: ${status}`;
}

/**
 * Generate unique ID for ARIA relationships
 */
let idCounter = 0;
export function generateAriaId(prefix: string = 'aria'): string {
  idCounter += 1;
  return `${prefix}-${idCounter}`;
}

/**
 * Check if element is keyboard focusable
 */
export function isFocusable(element: HTMLElement): boolean {
  if (element.tabIndex < 0) return false;
  if (element.hasAttribute('disabled')) return false;
  if (element.getAttribute('aria-hidden') === 'true') return false;
  
  const tagName = element.tagName.toLowerCase();
  const focusableTags = ['a', 'button', 'input', 'select', 'textarea'];
  
  return focusableTags.includes(tagName) || element.tabIndex >= 0;
}

/**
 * Get all focusable elements within a container
 */
export function getFocusableElements(container: HTMLElement): HTMLElement[] {
  const selector = [
    'a[href]',
    'button:not([disabled])',
    'input:not([disabled])',
    'select:not([disabled])',
    'textarea:not([disabled])',
    '[tabindex]:not([tabindex="-1"])',
  ].join(', ');
  
  return Array.from(container.querySelectorAll<HTMLElement>(selector));
}

/**
 * Skip to main content (for skip links)
 */
export function skipToMainContent(): void {
  const main = document.querySelector('main');
  if (main) {
    main.setAttribute('tabindex', '-1');
    main.focus();
    main.removeAttribute('tabindex');
  }
}

/**
 * Get accessible name for document
 * Combines filename, type, and status for screen readers
 */
export function getDocumentAccessibleName(document: {
  original_filename: string;
  file_type: string;
  processing_status: string;
}): string {
  const fileTypeLabel = getFileTypeAriaLabel(document.file_type);
  const statusLabel = getProcessingStatusAriaLabel(document.processing_status);
  
  return `${document.original_filename}, ${fileTypeLabel}, ${statusLabel}`;
}

/**
 * Format count for screen readers
 * Properly announces singular/plural
 */
export function formatCountForScreenReader(
  count: number,
  singular: string,
  plural?: string
): string {
  const pluralForm = plural || `${singular}s`;
  return count === 1 ? `${count} ${singular}` : `${count} ${pluralForm}`;
}
