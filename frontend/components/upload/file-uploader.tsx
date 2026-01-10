'use client';

import { useCallback, useState } from 'react';
import { Upload, X, File, CheckCircle2, AlertCircle } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import { apiClient } from '@/lib/api/client';
import { ApiError, UploadResponse } from '@/lib/api/types';
import { cn } from '@/lib/utils';

interface FileWithStatus {
  file: File;
  status: 'pending' | 'uploading' | 'success' | 'error';
  progress?: number;
  result?: UploadResponse;
  error?: string;
}

export function FileUploader() {
  const [files, setFiles] = useState<FileWithStatus[]>([]);
  const [isDragging, setIsDragging] = useState(false);

  const handleDrop = useCallback((e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setIsDragging(false);

    const droppedFiles = Array.from(e.dataTransfer.files);
    addFiles(droppedFiles);
  }, []);

  const handleDragOver = useCallback((e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setIsDragging(true);
  }, []);

  const handleDragLeave = useCallback(() => {
    setIsDragging(false);
  }, []);

  const handleFileSelect = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      const selectedFiles = Array.from(e.target.files);
      addFiles(selectedFiles);
    }
  }, []);

  const addFiles = (newFiles: File[]) => {
    const filesWithStatus: FileWithStatus[] = newFiles.map((file) => ({
      file,
      status: 'pending',
    }));
    setFiles((prev) => [...prev, ...filesWithStatus]);
  };

  const removeFile = (index: number) => {
    setFiles((prev) => prev.filter((_, i) => i !== index));
  };

  const uploadFile = async (index: number) => {
    setFiles((prev) =>
      prev.map((f, i) => (i === index ? { ...f, status: 'uploading', progress: 0 } : f))
    );

    try {
      const result = await apiClient.uploadDocument(files[index].file);

      setFiles((prev) =>
        prev.map((f, i) =>
          i === index ? { ...f, status: 'success', progress: 100, result } : f
        )
      );
    } catch (error) {
      const errorMessage =
        error instanceof ApiError ? error.message : 'Upload failed';

      setFiles((prev) =>
        prev.map((f, i) =>
          i === index ? { ...f, status: 'error', error: errorMessage } : f
        )
      );
    }
  };

  const uploadAll = async () => {
    const pendingFiles = files
      .map((f, index) => ({ ...f, index }))
      .filter((f) => f.status === 'pending');

    for (const { index } of pendingFiles) {
      await uploadFile(index);
    }
  };

  const clearCompleted = () => {
    setFiles((prev) => prev.filter((f) => f.status !== 'success'));
  };

  return (
    <div className="space-y-6">
      {/* Drop Zone */}
      <div
        onDrop={handleDrop}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        className={cn(
          'border-2 border-dashed rounded-lg p-12 text-center transition-colors',
          isDragging
            ? 'border-primary bg-primary/5'
            : 'border-slate-300 dark:border-slate-700'
        )}
      >
        <Upload className="mx-auto h-12 w-12 text-slate-400 mb-4" />
        <h3 className="text-lg font-semibold mb-2">Drop files here</h3>
        <p className="text-sm text-slate-600 dark:text-slate-400 mb-4">
          or click to browse (PDF, DOCX, TXT up to 50MB)
        </p>
        <input
          type="file"
          id="file-input"
          className="hidden"
          multiple
          accept=".pdf,.docx,.txt"
          onChange={handleFileSelect}
        />
        <Button asChild>
          <label htmlFor="file-input">Select Files</label>
        </Button>
      </div>

      {/* File List */}
      {files.length > 0 && (
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-lg font-semibold">
              Files ({files.length})
            </h3>
            <div className="flex gap-2">
              <Button
                onClick={uploadAll}
                disabled={!files.some((f) => f.status === 'pending')}
              >
                Upload All
              </Button>
              <Button variant="outline" onClick={clearCompleted}>
                Clear Completed
              </Button>
            </div>
          </div>

          <div className="space-y-2">
            {files.map((fileWithStatus, index) => (
              <Card key={index}>
                <CardContent className="p-4">
                  <div className="flex items-center gap-4">
                    <File className="h-8 w-8 text-slate-400" />
                    
                    <div className="flex-1 min-w-0">
                      <p className="font-medium truncate">
                        {fileWithStatus.file.name}
                      </p>
                      <p className="text-sm text-slate-600 dark:text-slate-400">
                        {(fileWithStatus.file.size / 1024 / 1024).toFixed(2)} MB
                      </p>
                      {fileWithStatus.error && (
                        <p className="text-sm text-red-600 mt-1">
                          {fileWithStatus.error}
                        </p>
                      )}
                      {fileWithStatus.result && (
                        <p className="text-sm text-green-600 mt-1">
                          Uploaded • Job ID: {fileWithStatus.result.job_id}
                        </p>
                      )}
                    </div>

                    <div className="flex items-center gap-2">
                      {fileWithStatus.status === 'pending' && (
                        <Button
                          size="sm"
                          onClick={() => uploadFile(index)}
                        >
                          Upload
                        </Button>
                      )}
                      {fileWithStatus.status === 'uploading' && (
                        <div className="text-sm text-slate-600">
                          Uploading...
                        </div>
                      )}
                      {fileWithStatus.status === 'success' && (
                        <CheckCircle2 className="h-5 w-5 text-green-600" />
                      )}
                      {fileWithStatus.status === 'error' && (
                        <AlertCircle className="h-5 w-5 text-red-600" />
                      )}
                      <Button
                        size="sm"
                        variant="ghost"
                        onClick={() => removeFile(index)}
                      >
                        <X className="h-4 w-4" />
                      </Button>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
