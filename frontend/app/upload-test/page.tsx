'use client';

import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { apiClient } from '@/lib/api/client';

export default function UploadTestPage() {
  const [log, setLog] = useState<string[]>([]);
  const [testFile, setTestFile] = useState<File | null>(null);
  const [isUploading, setIsUploading] = useState(false);

  const addLog = (message: string) => {
    setLog((prev) => [...prev, `[${new Date().toLocaleTimeString()}] ${message}`]);
  };

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setTestFile(e.target.files[0]);
      addLog(`File selected: ${e.target.files[0].name} (${e.target.files[0].size} bytes)`);
    }
  };

  const testDirectUpload = async () => {
    if (!testFile) {
      addLog('ERROR: No file selected');
      return;
    }

    setIsUploading(true);
    addLog('Starting direct upload test...');

    try {
      const formData = new FormData();
      formData.append('file', testFile);
      formData.append('tenant_id', '1');
      formData.append('user_id', '1');

      addLog(`Sending request to: ${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/v1/documents/upload`);

      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/v1/documents/upload`, {
        method: 'POST',
        body: formData,
      });

      addLog(`Response status: ${response.status} ${response.statusText}`);
      addLog(`Response headers: ${JSON.stringify(Object.fromEntries(response.headers))}`);

      const responseText = await response.text();
      addLog(`Response body: ${responseText}`);

      if (response.ok) {
        const data = JSON.parse(responseText);
        addLog(`SUCCESS: Document uploaded with ID ${data.document_id}`);
      } else {
        addLog(`ERROR: Upload failed`);
      }
    } catch (error) {
      addLog(`EXCEPTION: ${error instanceof Error ? error.message : String(error)}`);
      console.error('Upload error:', error);
    } finally {
      setIsUploading(false);
    }
  };

  const testApiClientUpload = async () => {
    if (!testFile) {
      addLog('ERROR: No file selected');
      return;
    }

    setIsUploading(true);
    addLog('Starting ApiClient upload test...');

    try {
      const result = await apiClient.uploadDocument(testFile);
      addLog(`SUCCESS: Document uploaded via ApiClient`);
      addLog(`Result: ${JSON.stringify(result, null, 2)}`);
    } catch (error: any) {
      addLog(`ERROR: ${error.message || String(error)}`);
      addLog(`Error details: ${JSON.stringify(error, null, 2)}`);
      console.error('Upload error:', error);
    } finally {
      setIsUploading(false);
    }
  };

  const testHealthCheck = async () => {
    addLog('Testing API health...');
    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/v1/health`);
      addLog(`Health check status: ${response.status}`);
      const data = await response.json();
      addLog(`Health check result: ${JSON.stringify(data)}`);
    } catch (error) {
      addLog(`Health check failed: ${error instanceof Error ? error.message : String(error)}`);
    }
  };

  const clearLog = () => {
    setLog([]);
  };

  return (
    <div className="min-h-screen bg-slate-50 dark:bg-slate-950 p-8">
      <div className="max-w-4xl mx-auto space-y-6">
        <Card>
          <CardHeader>
            <CardTitle>Upload Diagnostic Tool</CardTitle>
            <CardDescription>
              Test file uploads and diagnose issues
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <label className="text-sm font-medium">Select Test File</label>
              <input
                type="file"
                onChange={handleFileSelect}
                className="block w-full text-sm text-slate-500
                  file:mr-4 file:py-2 file:px-4
                  file:rounded-md file:border-0
                  file:text-sm file:font-semibold
                  file:bg-primary file:text-primary-foreground
                  hover:file:bg-primary/90"
              />
              {testFile && (
                <p className="text-sm text-slate-600">
                  Selected: {testFile.name} ({testFile.size} bytes, {testFile.type})
                </p>
              )}
            </div>

            <div className="flex gap-2 flex-wrap">
              <Button onClick={testHealthCheck} variant="outline">
                Test API Health
              </Button>
              <Button onClick={testDirectUpload} disabled={!testFile || isUploading}>
                Test Direct Upload (fetch)
              </Button>
              <Button onClick={testApiClientUpload} disabled={!testFile || isUploading}>
                Test ApiClient Upload
              </Button>
              <Button onClick={clearLog} variant="outline">
                Clear Log
              </Button>
            </div>

            <div className="mt-4">
              <h3 className="text-sm font-medium mb-2">Configuration:</h3>
              <pre className="bg-slate-100 dark:bg-slate-800 p-3 rounded text-xs overflow-auto">
                API URL: {process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}
                {'\n'}Tenant ID: 1
                {'\n'}User ID: 1
              </pre>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Diagnostic Log</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="bg-black text-green-400 p-4 rounded font-mono text-xs h-96 overflow-auto">
              {log.length === 0 ? (
                <p className="text-slate-500">No log entries yet. Run a test to see results.</p>
              ) : (
                log.map((entry, i) => (
                  <div key={i} className="mb-1">
                    {entry}
                  </div>
                ))
              )}
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
