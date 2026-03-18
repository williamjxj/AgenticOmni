'use client';

import Link from 'next/link';
import { FileText, Search, Upload, Zap, CheckCircle2, ArrowRight, Database } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';

export default function HomePage() {
  return (
    <div className="min-h-screen bg-gradient-to-b from-slate-50 to-white dark:from-slate-950 dark:to-slate-900">
      {/* Hero Section */}
      <section className="container mx-auto px-4 py-16 md:py-24">
        <div className="max-w-4xl mx-auto text-center">
          <h1 className="text-4xl md:text-6xl font-bold mb-6 bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
            AI-Powered Document Intelligence
          </h1>
          <p className="text-xl md:text-2xl text-slate-600 dark:text-slate-300 mb-8">
            Upload markdown files, get instant answers through intelligent search
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Button size="lg" className="text-lg px-8" asChild>
              <Link href="/upload">
                <Upload className="mr-2 h-5 w-5" />
                Upload Documents
              </Link>
            </Button>
            <Button size="lg" variant="outline" className="text-lg px-8" asChild>
              <Link href="/search">
                <Search className="mr-2 h-5 w-5" />
                Search Documents
              </Link>
            </Button>
            <Button size="lg" variant="outline" className="text-lg px-8 border-purple-300 text-purple-700 hover:bg-purple-50 dark:border-purple-700 dark:text-purple-300 dark:hover:bg-purple-950" asChild>
              <Link href="/datasets">
                <Database className="mr-2 h-5 w-5" />
                HF Datasets
              </Link>
            </Button>
          </div>
        </div>
      </section>

      {/* How It Works */}
      <section className="container mx-auto px-4 py-16 bg-white dark:bg-slate-900">
        <div className="max-w-6xl mx-auto">
          <h2 className="text-3xl font-bold text-center mb-12">
            Simple 3-Step Process
          </h2>

          <div className="grid md:grid-cols-3 gap-8">
            {/* Step 1 */}
            <Card className="border-2">
              <CardHeader>
                <div className="w-12 h-12 rounded-full bg-blue-100 dark:bg-blue-900 flex items-center justify-center mb-4">
                  <Upload className="h-6 w-6 text-blue-600 dark:text-blue-300" />
                </div>
                <CardTitle className="flex items-center gap-2">
                  <span className="text-2xl font-bold text-blue-600">1</span>
                  Upload Markdown
                </CardTitle>
                <CardDescription>
                  Upload your markdown files (single file or entire folders)
                </CardDescription>
              </CardHeader>
              <CardContent>
                <ul className="space-y-2 text-sm text-slate-600 dark:text-slate-400">
                  <li className="flex items-center gap-2">
                    <CheckCircle2 className="h-4 w-4 text-green-600" />
                    Drag & drop support
                  </li>
                  <li className="flex items-center gap-2">
                    <CheckCircle2 className="h-4 w-4 text-green-600" />
                    Batch folder upload
                  </li>
                  <li className="flex items-center gap-2">
                    <CheckCircle2 className="h-4 w-4 text-green-600" />
                    English & Chinese support
                  </li>
                </ul>
              </CardContent>
            </Card>

            {/* Step 2 */}
            <Card className="border-2">
              <CardHeader>
                <div className="w-12 h-12 rounded-full bg-purple-100 dark:bg-purple-900 flex items-center justify-center mb-4">
                  <Zap className="h-6 w-6 text-purple-600 dark:text-purple-300" />
                </div>
                <CardTitle className="flex items-center gap-2">
                  <span className="text-2xl font-bold text-purple-600">2</span>
                  AI Processing
                </CardTitle>
                <CardDescription>
                  Automatic parsing and embedding generation
                </CardDescription>
              </CardHeader>
              <CardContent>
                <ul className="space-y-2 text-sm text-slate-600 dark:text-slate-400">
                  <li className="flex items-center gap-2">
                    <CheckCircle2 className="h-4 w-4 text-green-600" />
                    Extract structure & metadata
                  </li>
                  <li className="flex items-center gap-2">
                    <CheckCircle2 className="h-4 w-4 text-green-600" />
                    Generate semantic embeddings
                  </li>
                  <li className="flex items-center gap-2">
                    <CheckCircle2 className="h-4 w-4 text-green-600" />
                    Index for fast search
                  </li>
                </ul>
              </CardContent>
            </Card>

            {/* Step 3 */}
            <Card className="border-2">
              <CardHeader>
                <div className="w-12 h-12 rounded-full bg-green-100 dark:bg-green-900 flex items-center justify-center mb-4">
                  <Search className="h-6 w-6 text-green-600 dark:text-green-300" />
                </div>
                <CardTitle className="flex items-center gap-2">
                  <span className="text-2xl font-bold text-green-600">3</span>
                  Search & Query
                </CardTitle>
                <CardDescription>
                  Ask questions and get instant answers
                </CardDescription>
              </CardHeader>
              <CardContent>
                <ul className="space-y-2 text-sm text-slate-600 dark:text-slate-400">
                  <li className="flex items-center gap-2">
                    <CheckCircle2 className="h-4 w-4 text-green-600" />
                    Semantic search
                  </li>
                  <li className="flex items-center gap-2">
                    <CheckCircle2 className="h-4 w-4 text-green-600" />
                    Natural language queries
                  </li>
                  <li className="flex items-center gap-2">
                    <CheckCircle2 className="h-4 w-4 text-green-600" />
                    Ranked results
                  </li>
                </ul>
              </CardContent>
            </Card>
          </div>
        </div>
      </section>

      {/* Features */}
      <section className="container mx-auto px-4 py-16">
        <div className="max-w-6xl mx-auto">
          <h2 className="text-3xl font-bold text-center mb-12">
            Powerful Features
          </h2>

          <div className="grid md:grid-cols-2 gap-6">
            <Card>
              <CardHeader>
                <FileText className="h-8 w-8 mb-2 text-blue-600" />
                <CardTitle>Markdown-First</CardTitle>
                <CardDescription>
                  Optimized for markdown documentation, notes, and knowledge bases
                </CardDescription>
              </CardHeader>
              <CardContent className="text-sm text-slate-600 dark:text-slate-400">
                Preserves markdown structure including headings, code blocks, links, and tables
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <Zap className="h-8 w-8 mb-2 text-purple-600" />
                <CardTitle>Intelligent Embeddings</CardTitle>
                <CardDescription>
                  Multilingual semantic understanding (English & Chinese)
                </CardDescription>
              </CardHeader>
              <CardContent className="text-sm text-slate-600 dark:text-slate-400">
                Powered by advanced AI models for accurate semantic search
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <Search className="h-8 w-8 mb-2 text-green-600" />
                <CardTitle>Fast Search</CardTitle>
                <CardDescription>
                  Vector-based similarity search with sub-second response times
                </CardDescription>
              </CardHeader>
              <CardContent className="text-sm text-slate-600 dark:text-slate-400">
                Find relevant content even when exact keywords don't match
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CheckCircle2 className="h-8 w-8 mb-2 text-orange-600" />
                <CardTitle>Batch Processing</CardTitle>
                <CardDescription>
                  Upload entire folders of markdown files at once
                </CardDescription>
              </CardHeader>
              <CardContent className="text-sm text-slate-600 dark:text-slate-400">
                Process hundreds of documents in a single operation
              </CardContent>
            </Card>
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="container mx-auto px-4 py-16 bg-gradient-to-r from-blue-600 to-purple-600 rounded-2xl my-16">
        <div className="max-w-3xl mx-auto text-center text-white">
          <h2 className="text-3xl md:text-4xl font-bold mb-4">
            Ready to Get Started?
          </h2>
          <p className="text-xl mb-8 text-blue-100">
            Upload your markdown files and start searching in seconds
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Button size="lg" variant="secondary" className="text-lg px-8" asChild>
              <Link href="/upload">
                Start Uploading
                <ArrowRight className="ml-2 h-5 w-5" />
              </Link>
            </Button>
            <Button size="lg" variant="outline" className="text-lg px-8 bg-white/10 border-white/20 text-white hover:bg-white/20" asChild>
              <Link href="/documents">
                View My Documents
              </Link>
            </Button>
          </div>
        </div>
      </section>
    </div>
  );
}
