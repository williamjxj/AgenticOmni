import Link from 'next/link';
import { ArrowLeft, ExternalLink, Book, Code, Rocket } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';

export default function DocsPage() {
  return (
    <div className="min-h-screen bg-slate-50 dark:bg-slate-950">
      {/* Header */}
      <header className="border-b bg-white dark:bg-slate-900">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center gap-4">
            <Button variant="ghost" size="sm" asChild>
              <Link href="/">
                <ArrowLeft className="h-4 w-4 mr-2" />
                Back
              </Link>
            </Button>
            <h1 className="text-2xl font-bold">Documentation</h1>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="container mx-auto px-4 py-8">
        <div className="max-w-4xl mx-auto space-y-8">
          {/* Overview */}
          <Card>
            <CardHeader>
              <CardTitle>AgenticOmni Documentation</CardTitle>
              <CardDescription>
                Complete guide to using the AgenticOmni document processing platform
              </CardDescription>
            </CardHeader>
            <CardContent>
              <p className="text-slate-600 dark:text-slate-400">
                AgenticOmni is an AI-powered document intelligence platform that transforms
                documents into searchable knowledge using an advanced ETL-to-RAG pipeline.
              </p>
            </CardContent>
          </Card>

          {/* Quick Links */}
          <div className="grid md:grid-cols-2 gap-6">
            <Card>
              <CardHeader>
                <div className="flex items-center gap-2">
                  <Book className="h-5 w-5" />
                  <CardTitle>Getting Started</CardTitle>
                </div>
              </CardHeader>
              <CardContent className="space-y-3">
                <Button variant="outline" className="w-full justify-between" asChild>
                  <Link href="/upload">
                    Upload Documents
                    <ExternalLink className="h-4 w-4" />
                  </Link>
                </Button>
                <Button variant="outline" className="w-full justify-between" asChild>
                  <Link href="/documents">
                    View Documents
                    <ExternalLink className="h-4 w-4" />
                  </Link>
                </Button>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <div className="flex items-center gap-2">
                  <Code className="h-5 w-5" />
                  <CardTitle>API Documentation</CardTitle>
                </div>
              </CardHeader>
              <CardContent className="space-y-3">
                <Button variant="outline" className="w-full justify-between" asChild>
                  <Link href="http://localhost:8000/api/v1/docs" target="_blank">
                    Swagger UI
                    <ExternalLink className="h-4 w-4" />
                  </Link>
                </Button>
                <Button variant="outline" className="w-full justify-between" asChild>
                  <Link href="http://localhost:8000/api/v1/redoc" target="_blank">
                    ReDoc
                    <ExternalLink className="h-4 w-4" />
                  </Link>
                </Button>
              </CardContent>
            </Card>
          </div>

          {/* Features */}
          <Card>
            <CardHeader>
              <CardTitle>Key Features</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <h3 className="font-semibold mb-2">📄 Multi-Format Upload</h3>
                <p className="text-sm text-slate-600 dark:text-slate-400">
                  Support for PDF, DOCX, and TXT files. Single uploads (50MB), batch uploads (1-10 files),
                  and resumable uploads for large files up to 5GB.
                </p>
              </div>

              <div>
                <h3 className="font-semibold mb-2">🤖 DeepSeek LLM Integration</h3>
                <p className="text-sm text-slate-600 dark:text-slate-400">
                  Cost-effective RAG with 32K context window. Documents are automatically chunked
                  into 512-token segments optimized for retrieval.
                </p>
              </div>

              <div>
                <h3 className="font-semibold mb-2">⚡ Async Processing</h3>
                <p className="text-sm text-slate-600 dark:text-slate-400">
                  Background document processing with real-time progress tracking. Upload multiple
                  documents and monitor their processing status.
                </p>
              </div>

              <div>
                <h3 className="font-semibold mb-2">🏢 Enterprise Ready</h3>
                <p className="text-sm text-slate-600 dark:text-slate-400">
                  Multi-tenant architecture, storage quotas, content deduplication,
                  and Prometheus-compatible metrics for monitoring.
                </p>
              </div>
            </CardContent>
          </Card>

          {/* API Endpoints */}
          <Card>
            <CardHeader>
              <CardTitle>API Endpoints</CardTitle>
              <CardDescription>
                Available REST API endpoints for document management
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4 text-sm font-mono">
                <div>
                  <div className="flex items-center gap-2 mb-1">
                    <span className="px-2 py-1 bg-green-100 dark:bg-green-900 text-green-800 dark:text-green-200 rounded text-xs font-semibold">
                      POST
                    </span>
                    <code>/api/v1/documents/upload</code>
                  </div>
                  <p className="text-xs text-slate-600 dark:text-slate-400 ml-16">
                    Upload a single document
                  </p>
                </div>

                <div>
                  <div className="flex items-center gap-2 mb-1">
                    <span className="px-2 py-1 bg-green-100 dark:bg-green-900 text-green-800 dark:text-green-200 rounded text-xs font-semibold">
                      POST
                    </span>
                    <code>/api/v1/documents/batch-upload</code>
                  </div>
                  <p className="text-xs text-slate-600 dark:text-slate-400 ml-16">
                    Upload multiple documents (1-10 files)
                  </p>
                </div>

                <div>
                  <div className="flex items-center gap-2 mb-1">
                    <span className="px-2 py-1 bg-blue-100 dark:bg-blue-900 text-blue-800 dark:text-blue-200 rounded text-xs font-semibold">
                      GET
                    </span>
                    <code>/api/v1/documents</code>
                  </div>
                  <p className="text-xs text-slate-600 dark:text-slate-400 ml-16">
                    List all documents with pagination
                  </p>
                </div>

                <div>
                  <div className="flex items-center gap-2 mb-1">
                    <span className="px-2 py-1 bg-blue-100 dark:bg-blue-900 text-blue-800 dark:text-blue-200 rounded text-xs font-semibold">
                      GET
                    </span>
                    <code>/api/v1/processing/jobs/:id</code>
                  </div>
                  <p className="text-xs text-slate-600 dark:text-slate-400 ml-16">
                    Get processing job status
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Support */}
          <Card>
            <CardHeader>
              <div className="flex items-center gap-2">
                <Rocket className="h-5 w-5" />
                <CardTitle>Need Help?</CardTitle>
              </div>
            </CardHeader>
            <CardContent className="space-y-2 text-sm">
              <p>
                <strong>Version:</strong> 0.2.0
              </p>
              <p>
                <strong>Backend:</strong> Python 3.12, FastAPI, PostgreSQL, Redis
              </p>
              <p>
                <strong>Frontend:</strong> Next.js 16, React 19, TypeScript, Tailwind CSS
              </p>
              <p className="pt-4">
                For technical support or questions, please refer to the API documentation
                or contact the development team.
              </p>
            </CardContent>
          </Card>
        </div>
      </main>
    </div>
  );
}
