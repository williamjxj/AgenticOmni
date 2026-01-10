'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { ArrowLeft, FileText, Download, RefreshCw } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import { apiClient } from '@/lib/api/client';
import { Document } from '@/lib/api/types';

export default function DocumentsPage() {
  const [documents, setDocuments] = useState<Document[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);

  const fetchDocuments = async () => {
    setLoading(true);
    setError(null);
    try {
      const result = await apiClient.listDocuments(page, 20);
      setDocuments(result.documents || []);
      setTotalPages(result.total_pages || 1);
    } catch (err) {
      setError('Failed to load documents');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDocuments();
  }, [page]);

  const getStatusBadge = (status: string) => {
    const badges: Record<string, string> = {
      uploaded: 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200',
      processing: 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200',
      completed: 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200',
      failed: 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200',
    };

    return (
      <span
        className={`px-2 py-1 rounded-full text-xs font-medium ${
          badges[status] || badges.uploaded
        }`}
      >
        {status}
      </span>
    );
  };

  const formatFileSize = (bytes: number) => {
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(2)} KB`;
    return `${(bytes / 1024 / 1024).toFixed(2)} MB`;
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleString();
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
              <h1 className="text-2xl font-bold">My Documents</h1>
            </div>
            <div className="flex gap-2">
              <Button variant="outline" size="sm" onClick={fetchDocuments}>
                <RefreshCw className="h-4 w-4 mr-2" />
                Refresh
              </Button>
              <Button asChild>
                <Link href="/upload">Upload Documents</Link>
              </Button>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="container mx-auto px-4 py-8">
        <div className="max-w-6xl mx-auto">
          {loading ? (
            <div className="text-center py-12">
              <RefreshCw className="h-8 w-8 animate-spin mx-auto mb-4" />
              <p>Loading documents...</p>
            </div>
          ) : error ? (
            <Card>
              <CardContent className="p-6 text-center">
                <p className="text-red-600">{error}</p>
                <Button className="mt-4" onClick={fetchDocuments}>
                  Try Again
                </Button>
              </CardContent>
            </Card>
          ) : documents.length === 0 ? (
            <Card>
              <CardContent className="p-12 text-center">
                <FileText className="h-12 w-12 mx-auto mb-4 text-slate-400" />
                <h3 className="text-lg font-semibold mb-2">No documents yet</h3>
                <p className="text-slate-600 dark:text-slate-400 mb-4">
                  Upload your first document to get started
                </p>
                <Button asChild>
                  <Link href="/upload">Upload Document</Link>
                </Button>
              </CardContent>
            </Card>
          ) : (
            <>
              <div className="space-y-4">
                {documents.map((doc) => (
                  <Card key={doc.document_id}>
                    <CardContent className="p-6">
                      <div className="flex items-start justify-between">
                        <div className="flex gap-4 flex-1">
                          <FileText className="h-8 w-8 text-slate-400 mt-1" />
                          <div className="flex-1 min-w-0">
                            <h3 className="font-semibold truncate mb-1">
                              {doc.original_filename}
                            </h3>
                            <div className="flex flex-wrap gap-4 text-sm text-slate-600 dark:text-slate-400">
                              <span>ID: {doc.document_id}</span>
                              <span>Size: {formatFileSize(doc.file_size)}</span>
                              <span>Type: {doc.file_type.toUpperCase()}</span>
                              {doc.page_count && <span>Pages: {doc.page_count}</span>}
                              {doc.language && <span>Language: {doc.language}</span>}
                            </div>
                            <p className="text-xs text-slate-500 mt-1">
                              Uploaded: {formatDate(doc.uploaded_at)}
                            </p>
                          </div>
                        </div>
                        <div className="flex items-center gap-3">
                          {getStatusBadge(doc.processing_status)}
                          <Button size="sm" variant="outline">
                            <Download className="h-4 w-4" />
                          </Button>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>

              {/* Pagination */}
              {totalPages > 1 && (
                <div className="flex justify-center gap-2 mt-8">
                  <Button
                    variant="outline"
                    onClick={() => setPage((p) => Math.max(1, p - 1))}
                    disabled={page === 1}
                  >
                    Previous
                  </Button>
                  <span className="px-4 py-2">
                    Page {page} of {totalPages}
                  </span>
                  <Button
                    variant="outline"
                    onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
                    disabled={page === totalPages}
                  >
                    Next
                  </Button>
                </div>
              )}
            </>
          )}
        </div>
      </main>
    </div>
  );
}
