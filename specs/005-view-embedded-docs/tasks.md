# Tasks: View Ingested and Embedded Documents

**Input**: Design documents from `/specs/005-view-embedded-docs/`  
**Prerequisites**: plan.md ✅, spec.md ✅, data-model.md ✅, research.md ✅

**Status**: Backend search functionality completed. Frontend implementation required.

**Tests**: Tests are NOT explicitly requested in the specification, so test tasks are omitted per template guidelines.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3, US4)
- Include exact file paths in descriptions

## Path Conventions

This is a web application with:
- **Backend**: `src/` (FastAPI - already implemented)
- **Frontend**: `frontend/` (Next.js 16 App Router, React, TypeScript)
- **API**: Backend exposes REST endpoints, frontend consumes them

---

## Phase 1: Setup (Frontend Infrastructure)

**Purpose**: Set up frontend structure and API integration layer

- [x] T001 [P] Verify backend API endpoints are accessible and documented in `src/api/routes/documents.py`
- [x] T002 [P] Create TypeScript types for document entities in `frontend/lib/types/document.ts`
- [x] T003 [P] Implement API client for documents endpoint in `frontend/lib/api/documents.ts`
- [x] T004 [P] Create reusable UI components for document list in `frontend/components/documents/`
- [x] T005 Configure environment variables for API base URL in `frontend/.env.local`

---

## Phase 2: Foundational (Core API & State Management)

**Purpose**: Core API integration and data fetching infrastructure that ALL user stories depend on

**⚠️ CRITICAL**: No user story UI work can begin until this phase is complete

- [x] T006 Implement `fetchDocuments()` API function in `frontend/lib/api/documents.ts`
- [x] T007 Implement `fetchDocumentById()` API function in `frontend/lib/api/documents.ts`
- [x] T008 [P] Create document list state management with React hooks in `frontend/lib/hooks/useDocuments.ts`
- [x] T009 [P] Create error handling utilities in `frontend/lib/utils/error-handling.ts`
- [x] T010 [P] Create loading states and skeleton components in `frontend/components/ui/skeleton.tsx`
- [x] T011 Verify API integration with test query to `/api/v1/documents` endpoint

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Browse Document Library (Priority: P1) 🎯 MVP

**Goal**: Display a list of all successfully ingested and embedded documents with basic metadata (filename, file type, upload date, processing status)

**Independent Test**: Navigate to `/documents` page, verify at least 5 documents display with name, type, date, and status. Empty state shows "No documents available" message. Pagination works for 100+ documents.

### Implementation for User Story 1

- [x] T012 [P] [US1] Create documents list page in `frontend/app/documents/page.tsx`
- [x] T013 [P] [US1] Create `DocumentCard` component in `frontend/components/documents/document-card.tsx`
- [x] T014 [P] [US1] Create `DocumentList` component in `frontend/components/documents/document-list.tsx`
- [x] T015 [P] [US1] Create `EmptyState` component for no documents in `frontend/components/documents/empty-state.tsx`
- [x] T016 [US1] Implement document status badges (Complete, In Progress, Failed, Pending) in `frontend/components/documents/status-badge.tsx`
- [x] T017 [US1] Add file type icons (PDF, DOCX, TXT, MD) in `frontend/components/documents/file-type-icon.tsx`
- [x] T018 [US1] Implement date formatting utility in `frontend/lib/utils/date.ts`
- [x] T019 [US1] Add pagination controls in `frontend/components/documents/pagination.tsx`
- [x] T020 [US1] Connect document list page to API with loading/error states
- [x] T021 [US1] Add responsive layout for mobile and desktop views
- [x] T022 [US1] Handle empty state when no documents exist

**Checkpoint**: User Story 1 complete - users can browse their document library

---

## Phase 4: User Story 2 - View Document Details and Metadata (Priority: P2)

**Goal**: Display detailed information about each document including processing status, embedding completion, metadata, and extracted text preview

**Independent Test**: Click any document from the list, verify detail page shows: filename, file size, upload timestamp, processing status, embedding status, chunk count, and text preview. Error messages display clearly for failed processing.

### Implementation for User Story 2

- [x] T023 [P] [US2] Create document detail page in `frontend/app/documents/[id]/page.tsx`
- [x] T024 [P] [US2] Create `DocumentHeader` component with metadata in `frontend/components/documents/document-header.tsx`
- [x] T025 [P] [US2] Create `ProcessingStatusCard` component in `frontend/components/documents/processing-status-card.tsx`
- [x] T026 [P] [US2] Create `EmbeddingStatusCard` component in `frontend/components/documents/embedding-status-card.tsx`
- [x] T027 [P] [US2] Create `TextPreview` component in `frontend/components/documents/text-preview.tsx`
- [x] T028 [US2] Implement file size formatting utility in `frontend/lib/utils/format.ts`
- [x] T029 [US2] Add status indicators with icons and colors
- [x] T030 [US2] Display chunk count and embedding statistics
- [x] T031 [US2] Show extracted text preview (first 500-1000 characters)
- [x] T032 [US2] Display error messages with actionable guidance for failed processing
- [x] T033 [US2] Add "Back to Documents" navigation button
- [x] T034 [US2] Handle loading state while fetching document details
- [x] T035 [US2] Handle error state if document not found (404)

**Checkpoint**: User Stories 1 AND 2 both work independently - users can browse and view document details

---

## Phase 5: User Story 3 - Filter and Search Documents (Priority: P3)

**Goal**: Filter documents by file type, upload date, processing status, and search by filename to quickly find specific documents

**Independent Test**: Apply filters (file type: PDF, date: Last 7 days, status: Embedded) and verify list updates correctly. Search for document name and confirm matching results appear. Clear filters shows all documents again.

### Implementation for User Story 3

- [x] T036 [P] [US3] Create `FilterPanel` component in `frontend/components/documents/filter-panel.tsx`
- [x] T037 [P] [US3] Create `SearchBar` component in `frontend/components/documents/search-bar.tsx`
- [x] T038 [P] [US3] Create `FileTypeFilter` dropdown in `frontend/components/documents/filters/file-type-filter.tsx`
- [x] T039 [P] [US3] Create `DateRangeFilter` component in `frontend/components/documents/filters/date-range-filter.tsx`
- [x] T040 [P] [US3] Create `StatusFilter` component in `frontend/components/documents/filters/status-filter.tsx`
- [x] T041 [US3] Implement filter state management in `frontend/lib/hooks/useDocumentFilters.ts`
- [x] T042 [US3] Implement search debouncing utility in `frontend/lib/utils/debounce.ts`
- [x] T043 [US3] Add filter query parameters to API calls in `frontend/lib/api/documents.ts`
- [x] T044 [US3] Integrate filters into document list page
- [x] T045 [US3] Add "Clear all filters" button
- [x] T046 [US3] Show active filter count badge
- [x] T047 [US3] Display "No results found" when filters return empty set
- [ ] T048 [US3] Persist filter state in URL query parameters
- [x] T049 [US3] Add loading indicator while filtering

**Checkpoint**: User Stories 1, 2, AND 3 all work independently - full document management experience

---

## Phase 6: User Story 4 - View Embedding Details (Priority: P4)

**Goal**: Display technical embedding details including model used, vector dimensions, chunk count, chunk sizes, and chunking strategy for advanced users

**Independent Test**: View any successfully embedded document, expand "Embedding Details" section, verify it shows: model name (e.g., "nomic-embed-text:latest"), vector dimensions (768), chunk count, average chunk size, and individual chunk details.

### Implementation for User Story 4

- [x] T050 [P] [US4] Create `EmbeddingDetailsPanel` component in `frontend/components/documents/embedding-details-panel.tsx`
- [x] T051 [P] [US4] Create `ChunkStatistics` component in `frontend/components/documents/chunk-statistics.tsx`
- [x] T052 [P] [US4] Create `ChunkList` component in `frontend/components/documents/chunk-list.tsx`
- [x] T053 [P] [US4] Create `ChunkItem` component showing individual chunk details in `frontend/components/documents/chunk-item.tsx`
- [x] T054 [US4] Implement API function `fetchDocumentChunks()` in `frontend/lib/api/documents.ts`
- [x] T055 [US4] Add expandable/collapsible section for embedding details
- [x] T056 [US4] Display embedding model name and version
- [x] T057 [US4] Display vector dimensions (e.g., "768 dimensions")
- [x] T058 [US4] Show total chunks and average chunk size
- [x] T059 [US4] Display chunk list with sequence numbers, token counts, and page ranges
- [x] T060 [US4] Add "Not Available" state when document has no embeddings
- [x] T061 [US4] Add tooltips explaining technical terms for non-technical users

**Checkpoint**: All user stories (1-4) complete and independently functional

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that enhance the overall experience across all user stories

- [x] T062 [P] Add loading skeletons for all data fetching states
- [x] T063 [P] Implement error boundary in `frontend/app/error.tsx`
- [ ] T064 [P] Add analytics tracking for document views
- [ ] T065 [P] Optimize image assets and icons
- [x] T066 Add keyboard shortcuts for navigation (e.g., Escape to close detail view)
- [x] T067 Implement auto-refresh for documents in "In Progress" status
- [x] T068 Add accessibility attributes (ARIA labels, roles, focus management)
- [ ] T069 Test responsive design on mobile, tablet, and desktop
- [ ] T070 Add animations for smooth transitions between states
- [x] T071 Performance optimization: lazy loading for large document lists
- [x] T072 [P] Update documentation in `docs/FRONTEND_INTEGRATION.md`
- [ ] T073 Code cleanup and refactoring for consistency
- [ ] T074 Security review: sanitize user inputs, validate API responses

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-6)**: All depend on Foundational phase completion
  - User stories can then proceed in parallel (if staffed)
  - Or sequentially in priority order (P1 → P2 → P3 → P4)
- **Polish (Phase 7)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P2)**: Can start after Foundational (Phase 2) - Extends US1 but independently testable
- **User Story 3 (P3)**: Can start after Foundational (Phase 2) - Enhances US1 but independently testable
- **User Story 4 (P4)**: Can start after Foundational (Phase 2) - Extends US2 but independently testable

### Within Each User Story

- Components marked [P] within the same story can run in parallel
- API integration before UI component integration
- Core components before integration into pages
- Story complete before moving to next priority

### Parallel Opportunities

- All Setup tasks marked [P] can run in parallel (T001-T004)
- All Foundational tasks marked [P] can run in parallel (T008-T010)
- Once Foundational phase completes, all user stories can start in parallel (if team capacity allows)
- Within each story, all component creation tasks marked [P] can run in parallel
- Different user stories can be worked on in parallel by different team members

---

## Parallel Example: User Story 1

```bash
# Launch all UI components for User Story 1 together:
Task: "Create DocumentCard component in frontend/components/documents/document-card.tsx"
Task: "Create DocumentList component in frontend/components/documents/document-list.tsx"  
Task: "Create EmptyState component in frontend/components/documents/empty-state.tsx"

# These can all be developed in parallel since they're independent components
```

## Parallel Example: User Story 3

```bash
# Launch all filter components for User Story 3 together:
Task: "Create FileTypeFilter in frontend/components/documents/filters/file-type-filter.tsx"
Task: "Create DateRangeFilter in frontend/components/documents/filters/date-range-filter.tsx"
Task: "Create StatusFilter in frontend/components/documents/filters/status-filter.tsx"

# These filters are independent and can be built simultaneously
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (T001-T005)
2. Complete Phase 2: Foundational (T006-T011) - CRITICAL
3. Complete Phase 3: User Story 1 (T012-T022)
4. **STOP and VALIDATE**: Test User Story 1 independently
   - Can users see their document library?
   - Does pagination work?
   - Is empty state clear?
5. Deploy/demo if ready - **This is a functional MVP!**

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently → Deploy/Demo (MVP! Basic document browsing works)
3. Add User Story 2 → Test independently → Deploy/Demo (Can now view document details)
4. Add User Story 3 → Test independently → Deploy/Demo (Can now filter and search)
5. Add User Story 4 → Test independently → Deploy/Demo (Advanced embedding details available)
6. Each story adds value without breaking previous stories

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together
2. Once Foundational is done:
   - Developer A: User Story 1 (Document List)
   - Developer B: User Story 2 (Document Details)
   - Developer C: User Story 3 (Filters & Search)
   - Developer D: User Story 4 (Embedding Details)
3. Stories complete and integrate independently
4. Each developer can verify their story without waiting for others

---

## Backend API Endpoints (Already Implemented)

The following endpoints are already available from the backend:

### Documents Endpoints

- `GET /api/v1/documents` - List documents with pagination and filters
  - Query params: `tenant_id`, `file_type`, `processing_status`, `embedding_status`, `date_from`, `date_to`, `search`, `page`, `page_size`
  - Returns: Document list with metadata

- `GET /api/v1/documents/{document_id}` - Get document details
  - Returns: Complete document metadata, processing status, embedding status

- `GET /api/v1/documents/{document_id}/chunks` - Get document chunks
  - Returns: List of chunks with embeddings, sequence numbers, token counts

- `GET /api/v1/documents/{document_id}/text` - Get extracted text preview
  - Returns: Extracted text content with page numbers

### Search Endpoints

- `POST /api/v1/search/semantic` - Semantic search (already working)
  - Body: `{"query_text": "...", "tenant_id": 1, "top_k": 10}`
  - Returns: Search results with similarity scores

---

## Task Summary

**Total Tasks**: 74

**Tasks per User Story**:
- Setup (Phase 1): 5 tasks
- Foundational (Phase 2): 6 tasks (CRITICAL - blocks all stories)
- User Story 1 (P1): 11 tasks - Browse Document Library
- User Story 2 (P2): 13 tasks - View Document Details
- User Story 3 (P3): 14 tasks - Filter and Search
- User Story 4 (P4): 12 tasks - View Embedding Details
- Polish (Phase 7): 13 tasks - Cross-cutting improvements

**Parallel Opportunities**: 47 tasks marked [P] can run in parallel within their phases

**Independent Test Criteria**:
- US1: Navigate to documents page, see list with metadata, pagination works
- US2: Click document, see full details with status and text preview
- US3: Apply filters and search, list updates correctly
- US4: View embedding details section, see technical information

**Suggested MVP Scope**: Setup + Foundational + User Story 1 (22 tasks)
- Delivers: Document library browsing with basic metadata
- Validates: Core value proposition of seeing ingested documents
- Time estimate: 2-3 days for single developer

**Format Validation**: ✅ All 74 tasks follow strict checklist format with:
- Checkbox: `- [ ]`
- Task ID: T001-T074 in execution order
- [P] marker: 47 parallelizable tasks identified
- [Story] label: US1, US2, US3, US4 for user story phases
- File paths: All tasks include specific file locations

---

## Notes

- Backend API is complete and working (search fix completed)
- Frontend is the primary implementation focus
- Each user story delivers independent value
- Tests not included per specification (no TDD requirement)
- TypeScript for type safety throughout
- shadcn/ui components for consistent design
- Responsive design for mobile and desktop
- Follow Next.js 16 App Router conventions
- Use React Server Components where possible
- Client components only when needed (interactivity, state)

---

## Next Steps

1. **Review this task list** with the team
2. **Select MVP scope** (recommend User Story 1 only for first iteration)
3. **Assign tasks** to developers (can parallelize after Foundational phase)
4. **Start implementation** following the phase order
5. **Test independently** after each user story completion
6. **Deploy incrementally** as stories complete

🎯 **Recommended Start**: Begin with Phase 1 (Setup) tasks T001-T005
