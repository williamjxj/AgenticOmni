/**
 * AgenticOmni Landing Page
 * 
 * This is the main landing page for the AgenticOmni application.
 * It displays the application overview and provides navigation to key features.
 */

import Link from "next/link";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { HealthStatus } from "@/components/health-status";

export default function HomePage() {
  return (
    <div className="min-h-screen bg-gradient-to-b from-slate-50 to-slate-100 dark:from-slate-950 dark:to-slate-900">
      {/* Header */}
      <header className="border-b bg-white/50 backdrop-blur-sm dark:bg-slate-950/50">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <h1 className="text-2xl font-bold text-slate-900 dark:text-slate-100">
              AgenticOmni
            </h1>
            <nav className="flex gap-4">
              <Button variant="ghost" asChild>
                <Link href="/docs">
                  Documentation
                </Link>
              </Button>
              <Button variant="outline" asChild>
                <Link href="http://localhost:8000/api/v1/docs" target="_blank" rel="noopener noreferrer">
                  API Docs
                </Link>
              </Button>
            </nav>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <main className="container mx-auto px-4 py-16">
        <div className="max-w-6xl mx-auto">
          {/* Hero Content */}
          <div className="text-center mb-16">
            <h2 className="text-5xl font-bold tracking-tight text-slate-900 dark:text-slate-100 mb-4">
              AI-Powered Document Intelligence
            </h2>
            <p className="text-xl text-slate-600 dark:text-slate-400 max-w-2xl mx-auto mb-8">
              Transform multi-media documents into searchable knowledge with our
              advanced ETL-to-RAG pipeline
            </p>
            <div className="flex gap-4 justify-center">
              <Button size="lg" asChild>
                <Link href="/upload">Get Started</Link>
              </Button>
              <Button size="lg" variant="outline" asChild>
                <Link href="/docs">Learn More</Link>
              </Button>
            </div>
          </div>

          {/* Health Status */}
          <div className="mb-16">
            <HealthStatus />
          </div>

          {/* Features */}
          <div className="grid md:grid-cols-3 gap-6 mb-16">
            <Card>
              <CardHeader>
                <CardTitle>📄 Multi-Format Upload</CardTitle>
                <CardDescription>
                  Single, batch, and resumable uploads up to 5GB
                </CardDescription>
              </CardHeader>
              <CardContent>
                <p className="text-sm text-slate-600 dark:text-slate-400">
                  Upload PDF, DOCX, and TXT files. Support for single files (50MB),
                  batch uploads (1-10 files), and resumable uploads for large files up to 5GB.
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>🤖 DeepSeek LLM Integration</CardTitle>
                <CardDescription>
                  Cost-effective RAG with 32K context window
                </CardDescription>
              </CardHeader>
              <CardContent>
                <p className="text-sm text-slate-600 dark:text-slate-400">
                  RAG-optimized document chunking with DeepSeek LLM integration.
                  Smart semantic chunking (512 tokens) with embedding support for semantic search.
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>⚡ Enterprise Performance</CardTitle>
                <CardDescription>
                  Async processing with real-time progress tracking
                </CardDescription>
              </CardHeader>
              <CardContent>
                <p className="text-sm text-slate-600 dark:text-slate-400">
                  Multi-tenant architecture with async processing, storage quotas,
                  byte-level progress tracking, and Prometheus-compatible metrics.
                </p>
              </CardContent>
            </Card>
          </div>

          {/* Tech Stack */}
          <Card>
            <CardHeader>
              <CardTitle>Technology Stack</CardTitle>
              <CardDescription>
                Built with modern, production-ready technologies
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                <div>
                  <h4 className="font-semibold mb-2">Backend</h4>
                  <ul className="space-y-1 text-slate-600 dark:text-slate-400">
                    <li>Python 3.12+</li>
                    <li>FastAPI</li>
                    <li>SQLAlchemy</li>
                    <li>PostgreSQL</li>
                  </ul>
                </div>
                <div>
                  <h4 className="font-semibold mb-2">AI/ML</h4>
                  <ul className="space-y-1 text-slate-600 dark:text-slate-400">
                    <li>DeepSeek LLM</li>
                    <li>Docling (IBM)</li>
                    <li>OpenAI Embeddings</li>
                    <li>Tiktoken</li>
                  </ul>
                </div>
                <div>
                  <h4 className="font-semibold mb-2">Frontend</h4>
                  <ul className="space-y-1 text-slate-600 dark:text-slate-400">
                    <li>Next.js 16</li>
                    <li>React 19</li>
                    <li>TypeScript</li>
                    <li>Tailwind CSS</li>
                  </ul>
                </div>
                <div>
                  <h4 className="font-semibold mb-2">Infrastructure</h4>
                  <ul className="space-y-1 text-slate-600 dark:text-slate-400">
                    <li>Docker</li>
                    <li>Redis</li>
                    <li>Dramatiq</li>
                    <li>pgvector</li>
                  </ul>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      </main>

      {/* Footer */}
      <footer className="border-t bg-white/50 backdrop-blur-sm dark:bg-slate-950/50 mt-16">
        <div className="container mx-auto px-4 py-8">
          <div className="text-center text-sm text-slate-600 dark:text-slate-400">
            <p>AgenticOmni v0.2.0 - AI-Powered Document Intelligence Platform</p>
            <p className="mt-2">
              Built with ❤️ by Best IT Consultants
            </p>
          </div>
        </div>
      </footer>
    </div>
  );
}
