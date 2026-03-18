/**
 * Date formatting utilities
 * Feature: 005-view-embedded-docs
 */

/**
 * Format date for display
 * 
 * @example
 * ```ts
 * formatDate('2024-01-15T10:30:00Z') // "Jan 15, 2024, 10:30 AM"
 * formatDate(null) // "N/A"
 * ```
 */
export function formatDate(
  dateString: string | Date | null | undefined,
  options?: Intl.DateTimeFormatOptions
): string {
  if (!dateString) {
    return 'N/A';
  }
  
  const date = typeof dateString === 'string' ? new Date(dateString) : dateString;
  
  // Check if date is invalid
  if (isNaN(date.getTime())) {
    return 'Invalid Date';
  }
  
  const defaultOptions: Intl.DateTimeFormatOptions = {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
    ...options,
  };

  return date.toLocaleString('en-US', defaultOptions);
}

/**
 * Format date as relative time (e.g., "2 hours ago", "3 days ago")
 * 
 * @example
 * ```ts
 * formatRelativeTime('2024-01-15T10:00:00Z') // "2 hours ago"
 * formatRelativeTime(null) // "N/A"
 * ```
 */
export function formatRelativeTime(dateString: string | Date | null | undefined): string {
  if (!dateString) {
    return 'N/A';
  }
  
  const date = typeof dateString === 'string' ? new Date(dateString) : dateString;
  
  // Check if date is invalid
  if (isNaN(date.getTime())) {
    return 'Invalid Date';
  }
  
  const now = new Date();
  const diffMs = now.getTime() - date.getTime();
  const diffSec = Math.floor(diffMs / 1000);
  const diffMin = Math.floor(diffSec / 60);
  const diffHour = Math.floor(diffMin / 60);
  const diffDay = Math.floor(diffHour / 24);
  const diffWeek = Math.floor(diffDay / 7);
  const diffMonth = Math.floor(diffDay / 30);
  const diffYear = Math.floor(diffDay / 365);

  if (diffSec < 60) {
    return 'just now';
  } else if (diffMin < 60) {
    return `${diffMin} ${diffMin === 1 ? 'minute' : 'minutes'} ago`;
  } else if (diffHour < 24) {
    return `${diffHour} ${diffHour === 1 ? 'hour' : 'hours'} ago`;
  } else if (diffDay < 7) {
    return `${diffDay} ${diffDay === 1 ? 'day' : 'days'} ago`;
  } else if (diffWeek < 4) {
    return `${diffWeek} ${diffWeek === 1 ? 'week' : 'weeks'} ago`;
  } else if (diffMonth < 12) {
    return `${diffMonth} ${diffMonth === 1 ? 'month' : 'months'} ago`;
  } else {
    return `${diffYear} ${diffYear === 1 ? 'year' : 'years'} ago`;
  }
}

/**
 * Format date as short date (e.g., "Jan 15, 2024")
 * 
 * @example
 * ```ts
 * formatShortDate('2024-01-15T10:30:00Z') // "Jan 15, 2024"
 * formatShortDate(null) // "N/A"
 * ```
 */
export function formatShortDate(dateString: string | Date | null | undefined): string {
  if (!dateString) {
    return 'N/A';
  }
  
  const date = typeof dateString === 'string' ? new Date(dateString) : dateString;
  
  // Check if date is invalid
  if (isNaN(date.getTime())) {
    return 'Invalid Date';
  }
  
  return date.toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  });
}

/**
 * Format date as time only (e.g., "10:30 AM")
 * 
 * @example
 * ```ts
 * formatTime('2024-01-15T10:30:00Z') // "10:30 AM"
 * formatTime(null) // "N/A"
 * ```
 */
export function formatTime(dateString: string | Date | null | undefined): string {
  if (!dateString) {
    return 'N/A';
  }
  
  const date = typeof dateString === 'string' ? new Date(dateString) : dateString;
  
  // Check if date is invalid
  if (isNaN(date.getTime())) {
    return 'Invalid Date';
  }
  
  return date.toLocaleTimeString('en-US', {
    hour: '2-digit',
    minute: '2-digit',
  });
}

/**
 * Format date range (e.g., "Jan 15 - Jan 20, 2024")
 * 
 * @example
 * ```ts
 * formatDateRange('2024-01-15', '2024-01-20') // "Jan 15 - Jan 20, 2024"
 * formatDateRange(null, null) // "N/A"
 * ```
 */
export function formatDateRange(
  startDate: string | Date | null | undefined,
  endDate: string | Date | null | undefined
): string {
  if (!startDate || !endDate) {
    return 'N/A';
  }
  
  const start = typeof startDate === 'string' ? new Date(startDate) : startDate;
  const end = typeof endDate === 'string' ? new Date(endDate) : endDate;
  
  // Check if dates are invalid
  if (isNaN(start.getTime()) || isNaN(end.getTime())) {
    return 'Invalid Date';
  }

  const sameYear = start.getFullYear() === end.getFullYear();
  const sameMonth = sameYear && start.getMonth() === end.getMonth();

  if (sameMonth) {
    return `${start.toLocaleDateString('en-US', { month: 'short', day: 'numeric' })} - ${end.toLocaleDateString('en-US', { day: 'numeric', year: 'numeric' })}`;
  } else if (sameYear) {
    return `${start.toLocaleDateString('en-US', { month: 'short', day: 'numeric' })} - ${end.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })}`;
  } else {
    return `${start.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })} - ${end.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })}`;
  }
}

/**
 * Format ISO date string for datetime-local input
 * 
 * @example
 * ```ts
 * formatForInput('2024-01-15T10:30:00Z') // "2024-01-15T10:30"
 * formatForInput(null) // ""
 * ```
 */
export function formatForInput(dateString: string | Date | null | undefined): string {
  if (!dateString) {
    return '';
  }
  
  const date = typeof dateString === 'string' ? new Date(dateString) : dateString;
  
  // Check if date is invalid
  if (isNaN(date.getTime())) {
    return '';
  }
  
  const year = date.getFullYear();
  const month = String(date.getMonth() + 1).padStart(2, '0');
  const day = String(date.getDate()).padStart(2, '0');
  const hours = String(date.getHours()).padStart(2, '0');
  const minutes = String(date.getMinutes()).padStart(2, '0');
  
  return `${year}-${month}-${day}T${hours}:${minutes}`;
}

/**
 * Check if date is today
 */
export function isToday(dateString: string | Date | null | undefined): boolean {
  if (!dateString) {
    return false;
  }
  
  const date = typeof dateString === 'string' ? new Date(dateString) : dateString;
  
  // Check if date is invalid
  if (isNaN(date.getTime())) {
    return false;
  }
  
  const today = new Date();
  
  return (
    date.getDate() === today.getDate() &&
    date.getMonth() === today.getMonth() &&
    date.getFullYear() === today.getFullYear()
  );
}

/**
 * Check if date is yesterday
 */
export function isYesterday(dateString: string | Date | null | undefined): boolean {
  if (!dateString) {
    return false;
  }
  
  const date = typeof dateString === 'string' ? new Date(dateString) : dateString;
  
  // Check if date is invalid
  if (isNaN(date.getTime())) {
    return false;
  }
  
  const yesterday = new Date();
  yesterday.setDate(yesterday.getDate() - 1);
  
  return (
    date.getDate() === yesterday.getDate() &&
    date.getMonth() === yesterday.getMonth() &&
    date.getFullYear() === yesterday.getFullYear()
  );
}

/**
 * Format date with smart relative/absolute logic
 * Shows "just now", "today", "yesterday", or full date
 * 
 * @example
 * ```ts
 * formatSmartDate('2024-01-15T10:30:00Z') 
 * // If today: "Today at 10:30 AM"
 * // If yesterday: "Yesterday at 10:30 AM"
 * // Otherwise: "Jan 15, 2024"
 * formatSmartDate(null) // "N/A"
 * ```
 */
export function formatSmartDate(dateString: string | Date | null | undefined): string {
  if (!dateString) {
    return 'N/A';
  }
  
  const date = typeof dateString === 'string' ? new Date(dateString) : dateString;
  
  // Check if date is invalid
  if (isNaN(date.getTime())) {
    return 'Invalid Date';
  }
  
  if (isToday(date)) {
    return `Today at ${formatTime(date)}`;
  } else if (isYesterday(date)) {
    return `Yesterday at ${formatTime(date)}`;
  } else {
    const now = new Date();
    const diffDays = Math.floor((now.getTime() - date.getTime()) / (1000 * 60 * 60 * 24));
    
    if (diffDays < 7) {
      return formatRelativeTime(date);
    }
    
    return formatShortDate(date);
  }
}

/**
 * Get duration between two dates in human-readable format
 * 
 * @example
 * ```ts
 * getDuration('2024-01-15T10:00:00Z', '2024-01-15T11:30:00Z') // "1 hour 30 minutes"
 * getDuration(null, null) // "N/A"
 * ```
 */
export function getDuration(
  startDate: string | Date | null | undefined,
  endDate: string | Date | null | undefined
): string {
  if (!startDate || !endDate) {
    return 'N/A';
  }
  
  const start = typeof startDate === 'string' ? new Date(startDate) : startDate;
  const end = typeof endDate === 'string' ? new Date(endDate) : endDate;
  
  // Check if dates are invalid
  if (isNaN(start.getTime()) || isNaN(end.getTime())) {
    return 'Invalid Date';
  }
  
  const diffMs = end.getTime() - start.getTime();
  const diffSec = Math.floor(diffMs / 1000);
  const diffMin = Math.floor(diffSec / 60);
  const diffHour = Math.floor(diffMin / 60);
  const diffDay = Math.floor(diffHour / 24);

  if (diffDay > 0) {
    const hours = diffHour % 24;
    return hours > 0 ? `${diffDay}d ${hours}h` : `${diffDay}d`;
  } else if (diffHour > 0) {
    const minutes = diffMin % 60;
    return minutes > 0 ? `${diffHour}h ${minutes}m` : `${diffHour}h`;
  } else if (diffMin > 0) {
    const seconds = diffSec % 60;
    return seconds > 0 ? `${diffMin}m ${seconds}s` : `${diffMin}m`;
  } else {
    return `${diffSec}s`;
  }
}
