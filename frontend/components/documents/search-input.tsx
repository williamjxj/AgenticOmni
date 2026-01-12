/**
 * Search Input Component
 * Search input with debouncing and clear functionality
 * Feature: 005-view-embedded-docs / User Story 3
 */

import { useState, useEffect, useRef } from 'react';
import { Search, X, Loader2 } from 'lucide-react';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { cn } from '@/lib/utils';

interface SearchInputProps {
  value?: string;
  onChange: (value: string) => void;
  placeholder?: string;
  debounceMs?: number;
  loading?: boolean;
  className?: string;
  size?: 'sm' | 'md' | 'lg';
  onClear?: () => void;
}

/**
 * Search Input Component with Debouncing
 * 
 * Features:
 * - Debounced input to reduce API calls
 * - Clear button
 * - Loading indicator
 * - Keyboard shortcuts (Escape to clear)
 * 
 * @example
 * ```tsx
 * <SearchInput
 *   value={searchQuery}
 *   onChange={(value) => setSearchQuery(value)}
 *   placeholder="Search documents..."
 *   debounceMs={300}
 * />
 * ```
 */
export function SearchInput({
  value = '',
  onChange,
  placeholder = 'Search documents...',
  debounceMs = 300,
  loading = false,
  className,
  size = 'md',
  onClear,
}: SearchInputProps) {
  const [localValue, setLocalValue] = useState(value);
  const debounceTimerRef = useRef<NodeJS.Timeout | null>(null);

  // Sync external value changes
  useEffect(() => {
    setLocalValue(value);
  }, [value]);

  // Handle input change with debouncing
  const handleChange = (newValue: string) => {
    setLocalValue(newValue);

    // Clear existing timer
    if (debounceTimerRef.current) {
      clearTimeout(debounceTimerRef.current);
    }

    // Set new timer
    debounceTimerRef.current = setTimeout(() => {
      onChange(newValue);
    }, debounceMs);
  };

  // Handle clear
  const handleClear = () => {
    setLocalValue('');
    onChange('');
    if (onClear) {
      onClear();
    }
  };

  // Handle keyboard shortcuts
  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Escape') {
      handleClear();
      e.currentTarget.blur();
    }
  };

  // Cleanup timer on unmount
  useEffect(() => {
    return () => {
      if (debounceTimerRef.current) {
        clearTimeout(debounceTimerRef.current);
      }
    };
  }, []);

  const sizeClasses = {
    sm: 'h-9 text-sm',
    md: 'h-10 text-base',
    lg: 'h-12 text-lg',
  };

  return (
    <div className={cn('relative', className)}>
      {/* Search Icon */}
      <div className="absolute left-3 top-1/2 -translate-y-1/2 pointer-events-none">
        {loading ? (
          <Loader2 className="h-4 w-4 text-slate-400 animate-spin" />
        ) : (
          <Search className="h-4 w-4 text-slate-400" />
        )}
      </div>

      {/* Input */}
      <Input
        type="text"
        value={localValue}
        onChange={(e) => handleChange(e.target.value)}
        onKeyDown={handleKeyDown}
        placeholder={placeholder}
        className={cn('pl-10 pr-10', sizeClasses[size])}
      />

      {/* Clear Button */}
      {localValue && (
        <Button
          variant="ghost"
          size="sm"
          onClick={handleClear}
          className="absolute right-1 top-1/2 -translate-y-1/2 h-8 w-8 p-0 hover:bg-slate-100 dark:hover:bg-slate-800"
          title="Clear search (Esc)"
        >
          <X className="h-4 w-4" />
        </Button>
      )}
    </div>
  );
}

/**
 * Search Bar with Suggestions
 * Enhanced search input with recent searches and suggestions
 */
export function SearchBarWithSuggestions({
  value = '',
  onChange,
  placeholder = 'Search documents...',
  recentSearches = [],
  onSelectRecent,
  className,
}: {
  value?: string;
  onChange: (value: string) => void;
  placeholder?: string;
  recentSearches?: string[];
  onSelectRecent?: (search: string) => void;
  className?: string;
}) {
  const [showSuggestions, setShowSuggestions] = useState(false);
  const [localValue, setLocalValue] = useState(value);
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    setLocalValue(value);
  }, [value]);

  const handleFocus = () => {
    if (recentSearches.length > 0) {
      setShowSuggestions(true);
    }
  };

  const handleBlur = () => {
    // Delay to allow click on suggestion
    setTimeout(() => setShowSuggestions(false), 200);
  };

  const handleSelectSuggestion = (search: string) => {
    setLocalValue(search);
    onChange(search);
    setShowSuggestions(false);
    if (onSelectRecent) {
      onSelectRecent(search);
    }
  };

  return (
    <div className={cn('relative', className)}>
      <SearchInput
        value={localValue}
        onChange={onChange}
        placeholder={placeholder}
      />

      {/* Recent Searches Dropdown */}
      {showSuggestions && recentSearches.length > 0 && (
        <div className="absolute top-full left-0 right-0 mt-2 bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-lg shadow-lg z-50 overflow-hidden">
          <div className="px-3 py-2 text-xs font-semibold text-slate-600 dark:text-slate-400 border-b border-slate-200 dark:border-slate-800">
            Recent Searches
          </div>
          <ul className="max-h-64 overflow-y-auto">
            {recentSearches.map((search, index) => (
              <li key={index}>
                <button
                  onClick={() => handleSelectSuggestion(search)}
                  className="w-full px-3 py-2 text-left text-sm hover:bg-slate-100 dark:hover:bg-slate-800 flex items-center gap-2"
                >
                  <Search className="h-3 w-3 text-slate-400" />
                  <span className="text-slate-700 dark:text-slate-300">
                    {search}
                  </span>
                </button>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}

/**
 * Compact Search Button
 * Expandable search input for mobile or compact layouts
 */
export function CompactSearchButton({
  value = '',
  onChange,
  placeholder = 'Search...',
  className,
}: {
  value?: string;
  onChange: (value: string) => void;
  placeholder?: string;
  className?: string;
}) {
  const [isExpanded, setIsExpanded] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    if (isExpanded && inputRef.current) {
      inputRef.current.focus();
    }
  }, [isExpanded]);

  if (!isExpanded) {
    return (
      <Button
        variant="outline"
        size="sm"
        onClick={() => setIsExpanded(true)}
        className={cn('gap-2', className)}
      >
        <Search className="h-4 w-4" />
        <span className="hidden sm:inline">Search</span>
      </Button>
    );
  }

  return (
    <div className={cn('flex items-center gap-2', className)}>
      <SearchInput
        value={value}
        onChange={onChange}
        placeholder={placeholder}
        size="sm"
        className="flex-1"
      />
      <Button
        variant="ghost"
        size="sm"
        onClick={() => {
          setIsExpanded(false);
          onChange('');
        }}
      >
        <X className="h-4 w-4" />
      </Button>
    </div>
  );
}
