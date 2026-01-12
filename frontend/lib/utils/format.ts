/**
 * Formatting utilities
 * Feature: 005-view-embedded-docs
 */

/**
 * Format file size for display
 * 
 * @example
 * ```ts
 * formatFileSize(1024) // "1.00 KB"
 * formatFileSize(1048576) // "1.00 MB"
 * ```
 */
export function formatFileSize(bytes: number): string {
  if (bytes === 0) return '0 B';
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(2)} KB`;
  if (bytes < 1024 * 1024 * 1024) return `${(bytes / (1024 * 1024)).toFixed(2)} MB`;
  return `${(bytes / (1024 * 1024 * 1024)).toFixed(2)} GB`;
}

/**
 * Format number with thousands separators
 * 
 * @example
 * ```ts
 * formatNumber(1234567) // "1,234,567"
 * ```
 */
export function formatNumber(num: number): string {
  return num.toLocaleString('en-US');
}

/**
 * Format percentage
 * 
 * @example
 * ```ts
 * formatPercentage(0.856) // "85.6%"
 * formatPercentage(0.856, 0) // "86%"
 * ```
 */
export function formatPercentage(value: number, decimals: number = 1): string {
  return `${(value * 100).toFixed(decimals)}%`;
}

/**
 * Format confidence score
 * 
 * @example
 * ```ts
 * formatConfidence(0.95) // "95%"
 * formatConfidence(0.856) // "86%"
 * ```
 */
export function formatConfidence(score: number): string {
  return formatPercentage(score, 0);
}

/**
 * Truncate text with ellipsis
 * 
 * @example
 * ```ts
 * truncateText("Hello World", 8) // "Hello..."
 * truncateText("Hi", 10) // "Hi"
 * ```
 */
export function truncateText(text: string, maxLength: number, suffix: string = '...'): string {
  if (text.length <= maxLength) return text;
  return text.substring(0, maxLength - suffix.length) + suffix;
}

/**
 * Truncate text in the middle (useful for filenames)
 * 
 * @example
 * ```ts
 * truncateMiddle("very-long-document-name.pdf", 20) // "very-lo...ame.pdf"
 * ```
 */
export function truncateMiddle(text: string, maxLength: number, separator: string = '...'): string {
  if (text.length <= maxLength) return text;
  
  const separatorLength = separator.length;
  const charsToShow = maxLength - separatorLength;
  const frontChars = Math.ceil(charsToShow / 2);
  const backChars = Math.floor(charsToShow / 2);
  
  return text.substring(0, frontChars) + separator + text.substring(text.length - backChars);
}

/**
 * Format duration in milliseconds to human-readable string
 * 
 * @example
 * ```ts
 * formatDuration(1500) // "1.5 seconds"
 * formatDuration(65000) // "1 minute 5 seconds"
 * ```
 */
export function formatDuration(milliseconds: number): string {
  const seconds = Math.floor(milliseconds / 1000);
  const minutes = Math.floor(seconds / 60);
  const hours = Math.floor(minutes / 60);
  const days = Math.floor(hours / 24);

  if (days > 0) {
    const remainingHours = hours % 24;
    return remainingHours > 0 ? `${days}d ${remainingHours}h` : `${days}d`;
  } else if (hours > 0) {
    const remainingMinutes = minutes % 60;
    return remainingMinutes > 0 ? `${hours}h ${remainingMinutes}m` : `${hours}h`;
  } else if (minutes > 0) {
    const remainingSeconds = seconds % 60;
    return remainingSeconds > 0 ? `${minutes}m ${remainingSeconds}s` : `${minutes}m`;
  } else if (seconds > 0) {
    const ms = milliseconds % 1000;
    return ms > 0 && seconds < 10 ? `${(milliseconds / 1000).toFixed(1)}s` : `${seconds}s`;
  } else {
    return `${milliseconds}ms`;
  }
}

/**
 * Format token count (abbreviates large numbers)
 * 
 * @example
 * ```ts
 * formatTokenCount(1500) // "1.5K"
 * formatTokenCount(1234567) // "1.2M"
 * ```
 */
export function formatTokenCount(count: number): string {
  if (count < 1000) return count.toString();
  if (count < 1000000) return `${(count / 1000).toFixed(1)}K`;
  return `${(count / 1000000).toFixed(1)}M`;
}

/**
 * Format chunk size range
 * 
 * @example
 * ```ts
 * formatChunkSizeRange(100, 500) // "100-500 tokens"
 * ```
 */
export function formatChunkSizeRange(min: number, max: number): string {
  return `${min}-${max} tokens`;
}

/**
 * Capitalize first letter of each word
 * 
 * @example
 * ```ts
 * capitalize("hello world") // "Hello World"
 * ```
 */
export function capitalize(text: string): string {
  return text
    .split(' ')
    .map(word => word.charAt(0).toUpperCase() + word.slice(1).toLowerCase())
    .join(' ');
}

/**
 * Convert snake_case to Title Case
 * 
 * @example
 * ```ts
 * snakeToTitle("embedding_model_name") // "Embedding Model Name"
 * ```
 */
export function snakeToTitle(text: string): string {
  return text
    .split('_')
    .map(word => word.charAt(0).toUpperCase() + word.slice(1).toLowerCase())
    .join(' ');
}

/**
 * Format vector dimensions
 * 
 * @example
 * ```ts
 * formatVectorDimensions(768) // "768-dimensional"
 * ```
 */
export function formatVectorDimensions(dimensions: number): string {
  return `${dimensions}-dimensional`;
}

/**
 * Format model name (clean up common model naming patterns)
 * 
 * @example
 * ```ts
 * formatModelName("nomic-embed-text:latest") // "Nomic Embed Text (latest)"
 * ```
 */
export function formatModelName(modelName: string): string {
  const [name, version] = modelName.split(':');
  const cleanedName = name
    .split('-')
    .map(word => word.charAt(0).toUpperCase() + word.slice(1))
    .join(' ');
  
  return version ? `${cleanedName} (${version})` : cleanedName;
}

/**
 * Format extraction method
 * 
 * @example
 * ```ts
 * formatExtractionMethod("ocr_paddleocr") // "OCR (PaddleOCR)"
 * ```
 */
export function formatExtractionMethod(method: string): string {
  if (method === 'native') return 'Native Extraction';
  if (method.startsWith('ocr_')) {
    const engine = method.replace('ocr_', '');
    return `OCR (${capitalize(engine)})`;
  }
  return capitalize(method);
}

/**
 * Pluralize word based on count
 * 
 * @example
 * ```ts
 * pluralize(1, "document") // "1 document"
 * pluralize(5, "document") // "5 documents"
 * pluralize(1, "category", "categories") // "1 category"
 * ```
 */
export function pluralize(
  count: number,
  singular: string,
  plural?: string
): string {
  const pluralForm = plural || `${singular}s`;
  return `${count} ${count === 1 ? singular : pluralForm}`;
}

/**
 * Format language code to full name
 * 
 * @example
 * ```ts
 * formatLanguage("en") // "English"
 * formatLanguage("zh") // "Chinese"
 * ```
 */
export function formatLanguage(code: string): string {
  const languages: Record<string, string> = {
    en: 'English',
    es: 'Spanish',
    fr: 'French',
    de: 'German',
    it: 'Italian',
    pt: 'Portuguese',
    ru: 'Russian',
    ja: 'Japanese',
    ko: 'Korean',
    zh: 'Chinese',
    ar: 'Arabic',
    hi: 'Hindi',
  };
  
  return languages[code.toLowerCase()] || code.toUpperCase();
}
