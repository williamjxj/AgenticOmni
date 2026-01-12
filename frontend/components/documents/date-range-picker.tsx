/**
 * Date Range Picker Component
 * Select date ranges for filtering documents
 * Feature: 005-view-embedded-docs / User Story 3
 */

import { useState } from 'react';
import { Calendar, X } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { cn } from '@/lib/utils';
import { formatShortDate } from '@/lib/utils/date';

interface DateRangePickerProps {
  startDate?: string;
  endDate?: string;
  onRangeChange: (startDate?: string, endDate?: string) => void;
  className?: string;
}

/**
 * Date Range Picker Component
 * 
 * Provides:
 * - Start and end date selection
 * - Preset date ranges (Today, Week, Month, Year)
 * - Clear date range
 * - Date validation
 * 
 * @example
 * ```tsx
 * <DateRangePicker
 *   startDate={filters.date_from}
 *   endDate={filters.date_to}
 *   onRangeChange={(start, end) => {
 *     setFilters({ ...filters, date_from: start, date_to: end });
 *   }}
 * />
 * ```
 */
export function DateRangePicker({
  startDate,
  endDate,
  onRangeChange,
  className,
}: DateRangePickerProps) {
  const [localStartDate, setLocalStartDate] = useState(startDate || '');
  const [localEndDate, setLocalEndDate] = useState(endDate || '');

  const handleStartDateChange = (date: string) => {
    setLocalStartDate(date);
    onRangeChange(date || undefined, localEndDate || undefined);
  };

  const handleEndDateChange = (date: string) => {
    setLocalEndDate(date);
    onRangeChange(localStartDate || undefined, date || undefined);
  };

  const handleClear = () => {
    setLocalStartDate('');
    setLocalEndDate('');
    onRangeChange(undefined, undefined);
  };

  const handlePreset = (preset: 'today' | 'week' | 'month' | 'year') => {
    const now = new Date();
    const today = now.toISOString().split('T')[0];
    
    let start = today;
    
    switch (preset) {
      case 'today':
        start = today;
        break;
      case 'week':
        const weekAgo = new Date(now);
        weekAgo.setDate(weekAgo.getDate() - 7);
        start = weekAgo.toISOString().split('T')[0];
        break;
      case 'month':
        const monthAgo = new Date(now);
        monthAgo.setMonth(monthAgo.getMonth() - 1);
        start = monthAgo.toISOString().split('T')[0];
        break;
      case 'year':
        const yearAgo = new Date(now);
        yearAgo.setFullYear(yearAgo.getFullYear() - 1);
        start = yearAgo.toISOString().split('T')[0];
        break;
    }
    
    setLocalStartDate(start);
    setLocalEndDate(today);
    onRangeChange(start, today);
  };

  const hasDateRange = localStartDate || localEndDate;

  return (
    <div className={cn('space-y-4', className)}>
      <div className="flex items-center justify-between">
        <label className="text-sm font-semibold text-slate-900 dark:text-slate-100 flex items-center gap-2">
          <Calendar className="h-4 w-4" />
          Date Range
        </label>
        {hasDateRange && (
          <Button
            variant="ghost"
            size="sm"
            onClick={handleClear}
            className="text-xs h-auto py-1"
          >
            <X className="h-3 w-3 mr-1" />
            Clear
          </Button>
        )}
      </div>

      {/* Quick Presets */}
      <div className="grid grid-cols-2 gap-2">
        {[
          { value: 'today', label: 'Today' },
          { value: 'week', label: 'Last 7 days' },
          { value: 'month', label: 'Last 30 days' },
          { value: 'year', label: 'Last year' },
        ].map((preset) => (
          <Button
            key={preset.value}
            variant="outline"
            size="sm"
            onClick={() => handlePreset(preset.value as any)}
            className="text-xs"
          >
            {preset.label}
          </Button>
        ))}
      </div>

      {/* Date Inputs */}
      <div className="grid grid-cols-2 gap-3">
        <div>
          <label
            htmlFor="start-date"
            className="text-xs text-slate-600 dark:text-slate-400 mb-1 block"
          >
            From
          </label>
          <input
            id="start-date"
            type="date"
            value={localStartDate}
            onChange={(e) => handleStartDateChange(e.target.value)}
            max={localEndDate || undefined}
            className="w-full px-3 py-2 border border-slate-300 dark:border-slate-700 rounded-md bg-white dark:bg-slate-900 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>

        <div>
          <label
            htmlFor="end-date"
            className="text-xs text-slate-600 dark:text-slate-400 mb-1 block"
          >
            To
          </label>
          <input
            id="end-date"
            type="date"
            value={localEndDate}
            onChange={(e) => handleEndDateChange(e.target.value)}
            min={localStartDate || undefined}
            className="w-full px-3 py-2 border border-slate-300 dark:border-slate-700 rounded-md bg-white dark:bg-slate-900 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>
      </div>

      {/* Selected Range Display */}
      {hasDateRange && (
        <div className="text-xs text-slate-600 dark:text-slate-400 bg-slate-50 dark:bg-slate-900 rounded-md px-3 py-2">
          {localStartDate && localEndDate ? (
            <>
              <span className="font-medium">Range:</span>{' '}
              {formatShortDate(localStartDate)} - {formatShortDate(localEndDate)}
            </>
          ) : localStartDate ? (
            <>
              <span className="font-medium">After:</span>{' '}
              {formatShortDate(localStartDate)}
            </>
          ) : (
            <>
              <span className="font-medium">Before:</span>{' '}
              {formatShortDate(localEndDate)}
            </>
          )}
        </div>
      )}
    </div>
  );
}

/**
 * Compact Date Range Display
 * Shows selected date range as a badge/chip
 */
export function DateRangeDisplay({
  startDate,
  endDate,
  onClear,
  className,
}: {
  startDate?: string;
  endDate?: string;
  onClear?: () => void;
  className?: string;
}) {
  if (!startDate && !endDate) return null;

  return (
    <div
      className={cn(
        'inline-flex items-center gap-2 px-3 py-1 rounded-full bg-slate-100 dark:bg-slate-800 text-sm',
        className
      )}
    >
      <Calendar className="h-3 w-3 text-slate-600 dark:text-slate-400" />
      <span className="text-slate-700 dark:text-slate-300">
        {startDate && endDate
          ? `${formatShortDate(startDate)} - ${formatShortDate(endDate)}`
          : startDate
          ? `After ${formatShortDate(startDate)}`
          : `Before ${formatShortDate(endDate)}`}
      </span>
      {onClear && (
        <button
          onClick={onClear}
          className="hover:bg-slate-200 dark:hover:bg-slate-700 rounded-full p-0.5"
        >
          <X className="h-3 w-3" />
        </button>
      )}
    </div>
  );
}
