/**
 * Performance Optimization Utilities
 * Helper functions for improving application performance
 * Feature: 005-view-embedded-docs / Phase 7 - Polish
 */

/**
 * Debounce function
 * Delays function execution until after specified delay
 * 
 * @example
 * ```ts
 * const debouncedSearch = debounce((query) => search(query), 300);
 * ```
 */
export function debounce<T extends (...args: any[]) => any>(
  func: T,
  delay: number
): (...args: Parameters<T>) => void {
  let timeoutId: NodeJS.Timeout;
  
  return function debounced(...args: Parameters<T>) {
    clearTimeout(timeoutId);
    timeoutId = setTimeout(() => func(...args), delay);
  };
}

/**
 * Throttle function
 * Ensures function is only called at most once per specified interval
 * 
 * @example
 * ```ts
 * const throttledScroll = throttle(() => handleScroll(), 100);
 * ```
 */
export function throttle<T extends (...args: any[]) => any>(
  func: T,
  interval: number
): (...args: Parameters<T>) => void {
  let lastCall = 0;
  
  return function throttled(...args: Parameters<T>) {
    const now = Date.now();
    if (now - lastCall >= interval) {
      lastCall = now;
      func(...args);
    }
  };
}

/**
 * Lazy load image with Intersection Observer
 * 
 * @example
 * ```tsx
 * <img data-src="large-image.jpg" alt="..." />
 * lazyLoadImages();
 * ```
 */
export function lazyLoadImages(selector: string = 'img[data-src]'): () => void {
  const images = document.querySelectorAll<HTMLImageElement>(selector);
  
  const imageObserver = new IntersectionObserver((entries) => {
    entries.forEach((entry) => {
      if (entry.isIntersecting) {
        const img = entry.target as HTMLImageElement;
        const src = img.getAttribute('data-src');
        if (src) {
          img.src = src;
          img.removeAttribute('data-src');
          imageObserver.unobserve(img);
        }
      }
    });
  });
  
  images.forEach((img) => imageObserver.observe(img));
  
  return () => imageObserver.disconnect();
}

/**
 * Measure performance of a function
 * 
 * @example
 * ```ts
 * const result = measurePerformance('fetchData', () => fetchData());
 * console.log(`Took ${result.duration}ms`);
 * ```
 */
export function measurePerformance<T>(
  label: string,
  fn: () => T
): { result: T; duration: number } {
  const start = performance.now();
  const result = fn();
  const duration = performance.now() - start;
  
  if (process.env.NODE_ENV === 'development') {
    console.log(`[Performance] ${label}: ${duration.toFixed(2)}ms`);
  }
  
  return { result, duration };
}

/**
 * Measure async performance
 */
export async function measureAsyncPerformance<T>(
  label: string,
  fn: () => Promise<T>
): Promise<{ result: T; duration: number }> {
  const start = performance.now();
  const result = await fn();
  const duration = performance.now() - start;
  
  if (process.env.NODE_ENV === 'development') {
    console.log(`[Performance] ${label}: ${duration.toFixed(2)}ms`);
  }
  
  return { result, duration };
}

/**
 * Memoize function results
 * Caches function results based on arguments
 * 
 * @example
 * ```ts
 * const expensiveCalculation = memoize((n: number) => {
 *   // expensive operation
 *   return result;
 * });
 * ```
 */
export function memoize<T extends (...args: any[]) => any>(
  fn: T,
  keyFn?: (...args: Parameters<T>) => string
): T {
  const cache = new Map<string, ReturnType<T>>();
  
  return ((...args: Parameters<T>) => {
    const key = keyFn ? keyFn(...args) : JSON.stringify(args);
    
    if (cache.has(key)) {
      return cache.get(key)!;
    }
    
    const result = fn(...args);
    cache.set(key, result);
    return result;
  }) as T;
}

/**
 * Batch multiple updates into a single render
 * Useful for updating state multiple times efficiently
 * 
 * @example
 * ```ts
 * batchUpdates(() => {
 *   setName('John');
 *   setAge(30);
 *   setEmail('john@example.com');
 * });
 * ```
 */
export function batchUpdates(fn: () => void): void {
  // In React 18+, updates are batched automatically
  // This is a fallback for older versions
  if (typeof requestAnimationFrame !== 'undefined') {
    requestAnimationFrame(fn);
  } else {
    fn();
  }
}

/**
 * Virtual scroll helper
 * Calculate visible items for large lists
 * 
 * @example
 * ```ts
 * const { start, end } = getVisibleRange({
 *   scrollTop: 500,
 *   containerHeight: 600,
 *   itemHeight: 50,
 *   totalItems: 1000,
 *   overscan: 5,
 * });
 * ```
 */
export function getVisibleRange({
  scrollTop,
  containerHeight,
  itemHeight,
  totalItems,
  overscan = 3,
}: {
  scrollTop: number;
  containerHeight: number;
  itemHeight: number;
  totalItems: number;
  overscan?: number;
}): { start: number; end: number; offsetTop: number } {
  const start = Math.max(0, Math.floor(scrollTop / itemHeight) - overscan);
  const visibleCount = Math.ceil(containerHeight / itemHeight);
  const end = Math.min(totalItems, start + visibleCount + overscan * 2);
  const offsetTop = start * itemHeight;
  
  return { start, end, offsetTop };
}

/**
 * Preload image
 * Useful for prefetching images before they're needed
 * 
 * @example
 * ```ts
 * preloadImage('/path/to/image.jpg').then(() => {
 *   console.log('Image loaded');
 * });
 * ```
 */
export function preloadImage(src: string): Promise<void> {
  return new Promise((resolve, reject) => {
    const img = new Image();
    img.onload = () => resolve();
    img.onerror = reject;
    img.src = src;
  });
}

/**
 * Prefetch data for next page
 * Useful for pagination - preload next page data
 * 
 * @example
 * ```ts
 * prefetchData(() => fetchDocuments(nextPage));
 * ```
 */
export function prefetchData<T>(
  fetcher: () => Promise<T>,
  delay: number = 0
): void {
  setTimeout(() => {
    fetcher().catch((err) => {
      console.warn('Prefetch failed:', err);
    });
  }, delay);
}

/**
 * Check if user prefers reduced motion
 * For accessibility - disable animations if requested
 */
export function prefersReducedMotion(): boolean {
  if (typeof window === 'undefined') return false;
  return window.matchMedia('(prefers-reduced-motion: reduce)').matches;
}

/**
 * Get optimal chunk size for batch processing
 * Prevents blocking UI with large operations
 * 
 * @example
 * ```ts
 * const chunkSize = getOptimalChunkSize(items.length);
 * for (let i = 0; i < items.length; i += chunkSize) {
 *   const chunk = items.slice(i, i + chunkSize);
 *   await processChunk(chunk);
 * }
 * ```
 */
export function getOptimalChunkSize(totalItems: number): number {
  if (totalItems < 100) return totalItems;
  if (totalItems < 1000) return 100;
  return 500;
}

/**
 * Run function in next idle period
 * Useful for non-critical work
 * 
 * @example
 * ```ts
 * runWhenIdle(() => {
 *   // Non-critical analytics or cleanup
 * });
 * ```
 */
export function runWhenIdle(
  fn: () => void,
  options?: IdleRequestOptions
): number {
  if ('requestIdleCallback' in window) {
    return requestIdleCallback(fn, options);
  }
  // Fallback for browsers without requestIdleCallback
  return setTimeout(fn, 1) as unknown as number;
}

/**
 * Cancel idle callback
 */
export function cancelIdle(id: number): void {
  if ('cancelIdleCallback' in window) {
    cancelIdleCallback(id);
  } else {
    clearTimeout(id);
  }
}
