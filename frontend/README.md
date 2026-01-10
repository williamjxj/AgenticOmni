# AgenticOmni Frontend

Next.js 16 frontend for the AgenticOmni document intelligence platform.

## Features

- ✅ **Modern Stack**: Next.js 16, React 19, TypeScript
- ✅ **Responsive UI**: Tailwind CSS with shadcn/ui components
- ✅ **Document Upload**: Drag-drop file uploader with progress tracking
- ✅ **Real-time Updates**: Job status polling with progress bars
- ✅ **Document Management**: List, view, and manage uploaded documents
- ✅ **Type-Safe API**: Complete TypeScript API client
- ✅ **Dark Mode**: Full dark mode support

## Getting Started

### 1. Install Dependencies

```bash
npm install
```

### 2. Configure Environment

Create a `.env.local` file (see `README_ENV.md` for details):

```bash
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
```

### 3. Start Backend

Ensure the backend is running on port 8000:

```bash
cd ..
source venv/bin/activate
uvicorn src.api.main:app --reload
```

### 4. Run Development Server

```bash
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) to view the application.

## Project Structure

```
frontend/
├── app/
│   ├── page.tsx              # Landing page
│   ├── upload/page.tsx       # Upload interface
│   ├── documents/page.tsx    # Document list
│   └── docs/page.tsx         # Documentation
├── components/
│   ├── upload/
│   │   ├── file-uploader.tsx      # Drag-drop uploader
│   │   └── progress-tracker.tsx   # Job progress
│   └── ui/                   # shadcn/ui components
├── lib/
│   ├── api/
│   │   ├── client.ts         # API client
│   │   └── types.ts          # TypeScript types
│   └── utils.ts              # Utility functions
└── README.md
```

## Available Pages

- **/** - Landing page with features overview
- **/upload** - Document upload interface with drag-drop
- **/documents** - View and manage uploaded documents
- **/docs** - Documentation and API reference

## API Integration

The frontend communicates with the backend via REST API. All API calls are handled through the centralized API client in `lib/api/client.ts`.

**Example:**
```typescript
import { apiClient } from '@/lib/api/client';

// Upload a document
const result = await apiClient.uploadDocument(file);

// Check job status
const status = await apiClient.getJobStatus(jobId);
```

See `docs/FRONTEND_INTEGRATION.md` in the project root for complete integration guide.

## Building for Production

```bash
npm run build
npm run start
```

## Tech Stack

- **Framework**: Next.js 16 with App Router
- **Language**: TypeScript
- **Styling**: Tailwind CSS 4
- **UI Components**: shadcn/ui (Radix UI primitives)
- **State**: React hooks (useState, useEffect)
- **API**: Fetch API with TypeScript client

## Features Demonstrated

### Document Upload
- Single file upload (up to 50MB)
- Drag and drop interface
- Multiple file selection
- Progress tracking
- Error handling

### Processing Status
- Real-time job status updates
- Progress bars with percentage
- Status badges (uploaded, processing, completed, failed)
- Automatic polling (2-second intervals)

### Document Management
- Paginated document list
- Status filtering
- File metadata display
- Responsive design

## Development Notes

- Uses Next.js Server Components by default
- Client components marked with `'use client'`
- All API calls are client-side
- Dark mode via Tailwind CSS
- Responsive design with mobile-first approach

## Version

**v0.2.0** - Document Upload & Processing MVP
