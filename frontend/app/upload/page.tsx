'use client';

import { useState } from 'react';
import Link from 'next/link';
import { ArrowLeft } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { FileUploader } from '@/components/upload/file-uploader';
import { ProgressTracker } from '@/components/upload/progress-tracker';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';

export default function UploadPage() {
  const [activeJobs, setActiveJobs] = useState<number[]>([]);

  const handleUploadComplete = (jobId: number) => {
    setActiveJobs((prev) => [...prev, jobId]);
  };

  return (
    <div className="min-h-screen bg-slate-50 dark:bg-slate-950">
      {/* Header */}
      <header className="border-b bg-white dark:bg-slate-900">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <Button variant="ghost" size="sm" asChild>
                <Link href="/">
                  <ArrowLeft className="h-4 w-4 mr-2" />
                  Back
                </Link>
              </Button>
              <h1 className="text-2xl font-bold">Upload Documents</h1>
            </div>
            <Button variant="outline" asChild>
              <Link href="/documents">View Documents</Link>
            </Button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="container mx-auto px-4 py-8">
        <div className="max-w-4xl mx-auto space-y-8">
          {/* Info Card */}
          <Card>
            <CardHeader>
              <CardTitle>Document Upload</CardTitle>
              <CardDescription>
                Upload documents for processing. Supported formats: PDF, DOCX, TXT (up to 50MB per file)
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid md:grid-cols-3 gap-4 text-sm">
                <div>
                  <p className="font-semibold mb-1">Single Upload</p>
                  <p className="text-slate-600 dark:text-slate-400">
                    Up to 50MB per file
                  </p>
                </div>
                <div>
                  <p className="font-semibold mb-1">Batch Upload</p>
                  <p className="text-slate-600 dark:text-slate-400">
                    1-10 files at once
                  </p>
                </div>
                <div>
                  <p className="font-semibold mb-1">Large Files</p>
                  <p className="text-slate-600 dark:text-slate-400">
                    Up to 5GB (resumable)
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* File Uploader */}
          <FileUploader />

          {/* Active Processing Jobs */}
          {activeJobs.length > 0 && (
            <div className="space-y-4">
              <h2 className="text-xl font-semibold">Processing</h2>
              <div className="space-y-4">
                {activeJobs.map((jobId) => (
                  <ProgressTracker
                    key={jobId}
                    jobId={jobId}
                    onComplete={(status) => {
                      console.log('Job completed:', status);
                    }}
                  />
                ))}
              </div>
            </div>
          )}

          {/* Tips */}
          <Card>
            <CardHeader>
              <CardTitle>Upload Tips</CardTitle>
            </CardHeader>
            <CardContent className="space-y-2 text-sm text-slate-600 dark:text-slate-400">
              <p>• Drag and drop multiple files or click to browse</p>
              <p>• Supported formats: PDF, DOCX, TXT</p>
              <p>• Files are processed asynchronously in the background</p>
              <p>• Processing time depends on file size and complexity</p>
              <p>• You can upload more files while others are processing</p>
            </CardContent>
          </Card>
        </div>
      </main>
    </div>
  );
}
