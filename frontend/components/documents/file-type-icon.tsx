/**
 * File Type Icon Component
 * Displays appropriate icon and color for different file types
 * Feature: 005-view-embedded-docs / User Story 1
 */

import {
  FileText,
  FileType,
  File,
  FileImage,
  FileSpreadsheet,
  FileCode,
  FileArchive,
  FileVideo,
  FileAudio,
} from 'lucide-react';
import { cn } from '@/lib/utils';

interface FileTypeIconProps {
  fileType: string;
  size?: 'sm' | 'md' | 'lg' | 'xl';
  className?: string;
  showBackground?: boolean;
}

interface FileTypeConfig {
  icon: React.ComponentType<{ className?: string }>;
  color: string;
  bgColor: string;
  label: string;
}

/**
 * Get file type configuration with icon, colors, and label
 */
function getFileTypeConfig(fileType: string): FileTypeConfig {
  const type = fileType.toLowerCase();

  const configs: Record<string, FileTypeConfig> = {
    // Documents
    pdf: {
      icon: FileType,
      color: 'text-red-600',
      bgColor: 'bg-red-100 dark:bg-red-900/30',
      label: 'PDF',
    },
    doc: {
      icon: FileText,
      color: 'text-blue-600',
      bgColor: 'bg-blue-100 dark:bg-blue-900/30',
      label: 'Word',
    },
    docx: {
      icon: FileText,
      color: 'text-blue-600',
      bgColor: 'bg-blue-100 dark:bg-blue-900/30',
      label: 'Word',
    },
    txt: {
      icon: FileText,
      color: 'text-slate-600',
      bgColor: 'bg-slate-100 dark:bg-slate-800',
      label: 'Text',
    },
    md: {
      icon: FileText,
      color: 'text-purple-600',
      bgColor: 'bg-purple-100 dark:bg-purple-900/30',
      label: 'Markdown',
    },
    markdown: {
      icon: FileText,
      color: 'text-purple-600',
      bgColor: 'bg-purple-100 dark:bg-purple-900/30',
      label: 'Markdown',
    },
    rtf: {
      icon: FileText,
      color: 'text-indigo-600',
      bgColor: 'bg-indigo-100 dark:bg-indigo-900/30',
      label: 'RTF',
    },

    // Spreadsheets
    xls: {
      icon: FileSpreadsheet,
      color: 'text-green-600',
      bgColor: 'bg-green-100 dark:bg-green-900/30',
      label: 'Excel',
    },
    xlsx: {
      icon: FileSpreadsheet,
      color: 'text-green-600',
      bgColor: 'bg-green-100 dark:bg-green-900/30',
      label: 'Excel',
    },
    csv: {
      icon: FileSpreadsheet,
      color: 'text-teal-600',
      bgColor: 'bg-teal-100 dark:bg-teal-900/30',
      label: 'CSV',
    },

    // Images
    jpg: {
      icon: FileImage,
      color: 'text-orange-600',
      bgColor: 'bg-orange-100 dark:bg-orange-900/30',
      label: 'Image',
    },
    jpeg: {
      icon: FileImage,
      color: 'text-orange-600',
      bgColor: 'bg-orange-100 dark:bg-orange-900/30',
      label: 'Image',
    },
    png: {
      icon: FileImage,
      color: 'text-pink-600',
      bgColor: 'bg-pink-100 dark:bg-pink-900/30',
      label: 'Image',
    },
    gif: {
      icon: FileImage,
      color: 'text-purple-600',
      bgColor: 'bg-purple-100 dark:bg-purple-900/30',
      label: 'Image',
    },
    webp: {
      icon: FileImage,
      color: 'text-indigo-600',
      bgColor: 'bg-indigo-100 dark:bg-indigo-900/30',
      label: 'Image',
    },
    svg: {
      icon: FileImage,
      color: 'text-yellow-600',
      bgColor: 'bg-yellow-100 dark:bg-yellow-900/30',
      label: 'SVG',
    },

    // Code
    html: {
      icon: FileCode,
      color: 'text-orange-600',
      bgColor: 'bg-orange-100 dark:bg-orange-900/30',
      label: 'HTML',
    },
    css: {
      icon: FileCode,
      color: 'text-blue-600',
      bgColor: 'bg-blue-100 dark:bg-blue-900/30',
      label: 'CSS',
    },
    js: {
      icon: FileCode,
      color: 'text-yellow-600',
      bgColor: 'bg-yellow-100 dark:bg-yellow-900/30',
      label: 'JavaScript',
    },
    ts: {
      icon: FileCode,
      color: 'text-blue-600',
      bgColor: 'bg-blue-100 dark:bg-blue-900/30',
      label: 'TypeScript',
    },
    json: {
      icon: FileCode,
      color: 'text-slate-600',
      bgColor: 'bg-slate-100 dark:bg-slate-800',
      label: 'JSON',
    },
    xml: {
      icon: FileCode,
      color: 'text-orange-600',
      bgColor: 'bg-orange-100 dark:bg-orange-900/30',
      label: 'XML',
    },

    // Archives
    zip: {
      icon: FileArchive,
      color: 'text-amber-600',
      bgColor: 'bg-amber-100 dark:bg-amber-900/30',
      label: 'Archive',
    },
    rar: {
      icon: FileArchive,
      color: 'text-amber-600',
      bgColor: 'bg-amber-100 dark:bg-amber-900/30',
      label: 'Archive',
    },
    '7z': {
      icon: FileArchive,
      color: 'text-amber-600',
      bgColor: 'bg-amber-100 dark:bg-amber-900/30',
      label: 'Archive',
    },

    // Media
    mp4: {
      icon: FileVideo,
      color: 'text-purple-600',
      bgColor: 'bg-purple-100 dark:bg-purple-900/30',
      label: 'Video',
    },
    avi: {
      icon: FileVideo,
      color: 'text-purple-600',
      bgColor: 'bg-purple-100 dark:bg-purple-900/30',
      label: 'Video',
    },
    mp3: {
      icon: FileAudio,
      color: 'text-cyan-600',
      bgColor: 'bg-cyan-100 dark:bg-cyan-900/30',
      label: 'Audio',
    },
    wav: {
      icon: FileAudio,
      color: 'text-cyan-600',
      bgColor: 'bg-cyan-100 dark:bg-cyan-900/30',
      label: 'Audio',
    },
  };

  return configs[type] || {
    icon: File,
    color: 'text-slate-600',
    bgColor: 'bg-slate-100 dark:bg-slate-800',
    label: 'File',
  };
}

/**
 * Get size classes for icon
 */
function getIconSize(size: 'sm' | 'md' | 'lg' | 'xl'): string {
  const sizes = {
    sm: 'h-4 w-4',
    md: 'h-6 w-6',
    lg: 'h-8 w-8',
    xl: 'h-12 w-12',
  };
  return sizes[size];
}

/**
 * Get padding classes for background
 */
function getBackgroundSize(size: 'sm' | 'md' | 'lg' | 'xl'): string {
  const sizes = {
    sm: 'p-1.5',
    md: 'p-2',
    lg: 'p-2.5',
    xl: 'p-3',
  };
  return sizes[size];
}

/**
 * File Type Icon Component
 * 
 * @example
 * ```tsx
 * <FileTypeIcon fileType="pdf" size="lg" showBackground />
 * <FileTypeIcon fileType="md" size="sm" />
 * <FileTypeIcon fileType="docx" />
 * ```
 */
export function FileTypeIcon({
  fileType,
  size = 'md',
  className,
  showBackground = false,
}: FileTypeIconProps) {
  const config = getFileTypeConfig(fileType);
  const Icon = config.icon;

  if (showBackground) {
    return (
      <div
        className={cn(
          'inline-flex items-center justify-center rounded-lg',
          config.bgColor,
          getBackgroundSize(size),
          className
        )}
        title={config.label}
      >
        <Icon className={cn(getIconSize(size), config.color)} />
      </div>
    );
  }

  return (
    <Icon
      className={cn(getIconSize(size), config.color, className)}
      title={config.label}
    />
  );
}

/**
 * File Type Label Component
 * Shows icon with text label
 */
export function FileTypeLabel({
  fileType,
  size = 'md',
  className,
}: Omit<FileTypeIconProps, 'showBackground'>) {
  const config = getFileTypeConfig(fileType);

  return (
    <div className={cn('inline-flex items-center gap-2', className)}>
      <FileTypeIcon fileType={fileType} size={size} showBackground />
      <span className="text-sm font-medium text-slate-700 dark:text-slate-300">
        {config.label}
      </span>
    </div>
  );
}

/**
 * Get file type color for custom styling
 */
export function getFileTypeColor(fileType: string): {
  color: string;
  bgColor: string;
} {
  const config = getFileTypeConfig(fileType);
  return {
    color: config.color,
    bgColor: config.bgColor,
  };
}
