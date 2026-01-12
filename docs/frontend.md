# Frontend Implementation Guide
## AI Document Management System - View Ingested and Embedded Documents

**Feature**: 005-view-embedded-docs  
**Last Updated**: 2026-01-12  
**Status**: ✅ Complete

---

## Table of Contents

1. [Overview](#overview)
2. [Architecture](#architecture)
3. [User Stories](#user-stories)
4. [Component Structure](#component-structure)
5. [API Integration](#api-integration)
6. [State Management](#state-management)
7. [Performance Optimizations](#performance-optimizations)
8. [Accessibility](#accessibility)
9. [Testing](#testing)
10. [Deployment](#deployment)

---

## Overview

This document describes the implementation of the frontend interface for viewing, filtering, and managing ingested documents with their embedding details.

### Technology Stack

- **Framework**: Next.js 16 (App Router)
- **UI Library**: React 18
- **Styling**: Tailwind CSS + Shadcn/UI
- **Type Safety**: TypeScript
- **State Management**: React Hooks (useState, useEffect, custom hooks)
- **API Client**: Native Fetch API with TypeScript

### Key Features

✅ **US1**: Browse document library with pagination  
✅ **US2**: View comprehensive document details  
✅ **US3**: Filter and search documents  
✅ **US4**: View embedding and chunk details

---

## Architecture

### Directory Structure

```
frontend/
├── app/                        # Next.js App Router pages
│   ├── documents/             # Document list page
│   │   ├── [id]/             # Document detail page
│   │   └── page.tsx
│   ├── error.tsx             # Error boundary
│   ├── global-error.tsx      # Global error boundary
│   └── layout.tsx
├── components/
│   ├── documents/            # Document-specific components
│   │   ├── document-card.tsx
│   │   ├── document-list.tsx
│   │   ├── document-header.tsx
│   │   ├── filter-panel.tsx
│   │   ├── search-input.tsx
│   │   ├── chunk-list.tsx
│   │   └── ...
│   └── ui/                   # Shadcn/UI components
│       ├── button.tsx
│       ├── card.tsx
│       └── ...
├── lib/
│   ├── api/                  # API client
│   │   ├── client.ts
│   │   ├── documents.ts
│   │   └── types.ts
│   ├── hooks/                # Custom React hooks
│   │   ├── useDocuments.ts
│   │   ├── useAutoRefresh.ts
│   │   └── ...
│   ├── types/                # TypeScript types
│   │   └── document.ts
│   └── utils/                # Utility functions
│       ├── date.ts
│       ├── format.ts
│       ├── error-handling.ts
│       ├── accessibility.ts
│       └── performance.ts
└── public/                   # Static assets
```

### Component Hierarchy

```
App Layout
└── Documents Page (/documents)
    ├── Header (with search & actions)
    ├── Filter Panel
    │   ├── Sort Controls
    │   ├── File Type Filters
    │   ├── Status Filters
    │   └── Date Range Picker
    ├── Active Filters (removable chips)
    ├── Document List
    │   └── Document Card (repeating)
    │       ├── File Type Icon
    │       ├── Status Badge
    │       └── Metadata
    └── Pagination

Document Detail Page (/documents/[id])
├── Document Header (metadata)
├── Processing Status Card
├── Embedding Status Card
├── Text Preview
└── Embedding Details Panel
    ├── Chunk Statistics
    └── Chunk List
        └── Chunk Item (repeating)
```

---

## User Stories

### US1: Browse Document Library (P1) ✅

**Goal**: Display paginated list of documents with basic metadata.

**Components**:
- `DocumentList` - Main list container
- `DocumentCard` - Individual document card
- `Pagination` - Page navigation
- `EmptyState` - No documents state
- `StatusBadge` - Processing status indicator
- `FileTypeIcon` - File type visualization

**API Endpoints**:
```typescript
GET /api/v1/documents?tenant_id=1&page=1&limit=20
```

**Key Features**:
- ✓ Responsive grid/list layout
- ✓ Status indicators (uploaded, parsing, parsed, failed)
- ✓ File type icons
- ✓ Upload date display
- ✓ Pagination (20 items per page)
- ✓ Empty state handling

---

### US2: View Document Details (P2) ✅

**Goal**: Show comprehensive document information including processing status and metadata.

**Components**:
- `DocumentHeader` - Document metadata display
- `ProcessingStatusCard` - Processing job details
- `EmbeddingStatusCard` - Embedding statistics
- `TextPreview` - Extracted text preview

**API Endpoints**:
```typescript
GET /api/v1/documents/{document_id}
GET /api/v1/documents/{document_id}/text-preview
```

**Key Features**:
- ✓ File metadata (size, type, dates)
- ✓ Processing status with timeline
- ✓ Embedding status with coverage %
- ✓ Text preview by page
- ✓ Error messages for failed processing
- ✓ Reprocess/regenerate actions

---

### US3: Filter & Search Documents (P3) ✅

**Goal**: Enable filtering by file type, status, dates, and search by name.

**Components**:
- `FilterPanel` - Collapsible filter controls
- `SearchInput` - Debounced search with autocomplete
- `DateRangePicker` - Date range selection
- `ActiveFilters` - Removable filter chips

**API Endpoints**:
```typescript
GET /api/v1/documents?tenant_id=1&file_type=pdf&status=parsed&search=query
```

**Key Features**:
- ✓ File type checkboxes (PDF, DOCX, TXT, MD, CSV)
- ✓ Processing status filters
- ✓ Embedding status filters
- ✓ Date range with presets
- ✓ Debounced search (300ms)
- ✓ Active filter display
- ✓ Clear all filters
- ✓ Sort by date/name/size

---

### US4: View Embedding Details (P4) ✅

**Goal**: Display technical embedding information for advanced users.

**Components**:
- `EmbeddingDetailsPanel` - Expandable details panel
- `ChunkStatistics` - Visual statistics
- `ChunkList` - Paginated chunk display
- `ChunkItem` - Individual chunk with metadata

**API Endpoints**:
```typescript
GET /api/v1/documents/{document_id}/embeddings/stats
GET /api/v1/documents/{document_id}/chunks?page=1&page_size=10
```

**Key Features**:
- ✓ Model name and version
- ✓ Vector dimensions (768D)
- ✓ Chunk statistics (count, avg size, coverage)
- ✓ Chunk list with pagination
- ✓ Token counts and page ranges
- ✓ Embedding status indicators
- ✓ Technical tooltips
- ✓ "Not available" state

---

## Component Structure

### Core Document Components

#### DocumentCard

```typescript
interface DocumentCardProps {
  document: Document;
  onDownload?: (documentId: number) => void;
  onClick?: (documentId: number) => void;
}
```

**Features**:
- File type icon with colors
- Processing & embedding status badges
- File size and metadata
- Upload date (relative time)
- Click to view details
- Download action

#### DocumentList

```typescript
interface DocumentListProps {
  documents: Document[];
  loading?: boolean;
  error?: string | null;
  emptyVariant?: 'no-documents' | 'no-results' | 'no-filtered-results';
  onDocumentClick?: (documentId: number) => void;
  onDocumentDownload?: (documentId: number) => void;
  onRetry?: () => void;
}
```

**Features**:
- Loading skeletons
- Empty states (contextual)
- Error handling with retry
- Grid/list layouts
- Responsive design

#### FilterPanel

```typescript
interface FilterPanelProps {
  filters: DocumentFilters;
  onFiltersChange: (filters: DocumentFilters) => void;
  sortOptions?: SortOptions;
  onSortChange?: (sort: SortOptions) => void;
  onClearFilters?: () => void;
}
```

**Features**:
- Collapsible panel
- Filter count badge
- Sort controls
- Checkbox filters
- Date range picker
- Clear all action

---

## API Integration

### API Client Structure

```typescript
// lib/api/documents.ts
export async function fetchDocuments(
  filters: DocumentFilters = {},
  sort?: SortOptions
): Promise<DocumentListResponse>

export async function fetchDocumentById(
  documentId: number,
  includeChunks?: boolean
): Promise<DocumentDetailResponse>

export async function fetchDocumentChunks(
  documentId: number,
  page: number,
  pageSize: number
): Promise<ChunkListResponse>
```

### Error Handling

```typescript
// lib/utils/error-handling.ts
- isApiError(error): Type guard
- getErrorMessage(error): User-friendly message
- getErrorSuggestions(error): Actionable suggestions
- retryWithBackoff(fn): Exponential backoff retry
```

### Response Types

```typescript
interface DocumentListResponse {
  documents: Document[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

interface Document {
  document_id: number;
  original_filename: string;
  file_type: string;
  file_size: number;
  processing_status: ProcessingStatus;
  embedding_status?: EmbeddingStatus;
  uploaded_at: string;
  // ... more fields
}
```

---

## State Management

### Custom Hooks

#### useDocuments

```typescript
const {
  documents,
  total,
  page,
  totalPages,
  loading,
  error,
  refetch,
  setPage,
  setFilters,
  setSort,
} = useDocuments({
  page: 1,
  page_size: 20,
});
```

**Features**:
- Automatic data fetching
- Pagination management
- Filter state management
- Loading/error states
- Refetch capability

#### useDocumentDetail

```typescript
const {
  document,
  loading,
  error,
  refetch,
} = useDocumentDetail(documentId, includeChunks);
```

#### useAutoRefresh

```typescript
useAutoRefresh({
  enabled: isProcessing,
  interval: 5000,
  onRefresh: () => refetchDocument(),
});
```

**Features**:
- Conditional auto-refresh
- Configurable interval
- Auto-stop when complete
- Exponential backoff variant
- Visibility-aware (pauses when tab inactive)

---

## Performance Optimizations

### 1. Code Splitting & Lazy Loading

```typescript
// Lazy load non-critical components
const EmbeddingDetailsPanel = dynamic(
  () => import('@/components/documents/embedding-details-panel'),
  { loading: () => <Skeleton /> }
);
```

### 2. Debouncing & Throttling

```typescript
// Search input with 300ms debounce
const debouncedSearch = debounce((query) => search(query), 300);
```

### 3. Memoization

```typescript
// Memoize expensive calculations
const filteredDocuments = useMemo(
  () => documents.filter(applyFilters),
  [documents, filters]
);
```

### 4. Virtual Scrolling

For large lists (>100 items), implement virtual scrolling:

```typescript
import { getVisibleRange } from '@/lib/utils/performance';

const { start, end } = getVisibleRange({
  scrollTop,
  containerHeight,
  itemHeight,
  totalItems,
  overscan: 5,
});
```

### 5. Image Optimization

- WebP format with fallbacks
- Lazy loading with Intersection Observer
- Responsive images with srcset

---

## Accessibility

### ARIA Attributes

```typescript
// Document cards
<article
  role="article"
  aria-label={getDocumentAccessibleName(document)}
>

// Status badges
<span
  role="status"
  aria-label={getProcessingStatusAriaLabel(status)}
>

// Interactive elements
<button
  aria-label="Filter documents"
  aria-expanded={isOpen}
  aria-controls="filter-panel"
>
```

### Keyboard Navigation

**Global Shortcuts**:
- `Shift + G` - Go to documents
- `Shift + H` - Go home
- `Shift + S` - Go to search
- `/` - Focus search input
- `Esc` - Clear search / Close modal

**Component Shortcuts**:
- `Enter` - Open document
- `Space` - Toggle selection
- `Arrow keys` - Navigate list

### Screen Reader Support

```typescript
// Announce dynamic changes
announceToScreenReader('Document uploaded successfully');

// Focus management
trapFocus(modalElement);
restoreFocus(previousElement);
```

### Color Contrast

All colors meet WCAG AA standards:
- Text: 4.5:1 contrast ratio
- Large text: 3:1 contrast ratio
- Interactive elements: 3:1 contrast ratio

---

## Testing

### Unit Tests

```typescript
// components/__tests__/document-card.test.tsx
describe('DocumentCard', () => {
  it('renders document information', () => {
    render(<DocumentCard document={mockDocument} />);
    expect(screen.getByText(mockDocument.filename)).toBeInTheDocument();
  });
  
  it('handles click events', () => {
    const onClick = jest.fn();
    render(<DocumentCard document={mockDocument} onClick={onClick} />);
    fireEvent.click(screen.getByRole('article'));
    expect(onClick).toHaveBeenCalledWith(mockDocument.document_id);
  });
});
```

### Integration Tests

```typescript
// app/__tests__/documents-page.test.tsx
describe('Documents Page', () => {
  it('fetches and displays documents', async () => {
    mockFetch(documents);
    render(<DocumentsPage />);
    
    await waitFor(() => {
      expect(screen.getAllByRole('article')).toHaveLength(documents.length);
    });
  });
});
```

### E2E Tests (Playwright)

```typescript
test('user can filter and search documents', async ({ page }) => {
  await page.goto('/documents');
  
  // Apply filter
  await page.click('[aria-label="Filter documents"]');
  await page.check('input[value="pdf"]');
  
  // Search
  await page.fill('input[type="search"]', 'report');
  
  // Verify results
  await expect(page.locator('[role="article"]')).toHaveCount(5);
});
```

---

## Deployment

### Environment Variables

```env
# .env.local
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_ANALYTICS_ID=your-analytics-id
```

### Build & Deploy

```bash
# Development
npm run dev

# Production build
npm run build

# Start production server
npm start
```

### Performance Metrics

Target metrics:
- **LCP** (Largest Contentful Paint): < 2.5s
- **FID** (First Input Delay): < 100ms
- **CLS** (Cumulative Layout Shift): < 0.1
- **TTI** (Time to Interactive): < 3.8s

---

## Best Practices

### 1. Type Safety

- Use TypeScript interfaces for all props
- Define API response types
- Avoid `any` types
- Use type guards for runtime checks

### 2. Error Handling

- Catch all async errors
- Display user-friendly messages
- Provide actionable suggestions
- Log errors to monitoring service

### 3. Loading States

- Show skeletons for content loading
- Disable buttons during actions
- Display progress indicators
- Handle slow connections gracefully

### 4. Responsive Design

- Mobile-first approach
- Test on multiple screen sizes
- Touch-friendly tap targets (44x44px min)
- Horizontal scrolling for tables

### 5. Security

- Sanitize user inputs
- Validate API responses
- Use HTTPS in production
- Implement CSP headers
- Rate limit API calls

---

## Troubleshooting

### Common Issues

**1. Documents not loading**
- Check API endpoint URL
- Verify backend is running
- Check network tab for errors
- Validate tenant_id parameter

**2. Filters not working**
- Check filter state management
- Verify API query parameters
- Clear browser cache
- Check for JavaScript errors

**3. Pagination issues**
- Verify total_pages calculation
- Check page parameter in URL
- Reset page on filter change
- Validate page bounds

**4. Performance issues**
- Enable React DevTools Profiler
- Check for unnecessary re-renders
- Implement memoization
- Use virtual scrolling for large lists

---

## Future Enhancements

### Planned Features

- [ ] Bulk actions (delete, export)
- [ ] Document comparison
- [ ] Advanced search with syntax
- [ ] Custom filter presets
- [ ] Drag & drop reordering
- [ ] Real-time collaboration
- [ ] Document annotations
- [ ] Export to PDF/CSV

### Technical Debt

- [ ] Add comprehensive E2E tests
- [ ] Implement error monitoring (Sentry)
- [ ] Add performance monitoring
- [ ] Optimize bundle size
- [ ] Add service worker for offline support

---

## Support & Contact

For questions or issues:
- **Documentation**: `/docs`
- **API Docs**: `/api/docs`
- **Issue Tracker**: GitHub Issues
- **Email**: support@example.com

---

**Last Updated**: 2026-01-12  
**Version**: 1.0.0  
**Contributors**: Development Team
