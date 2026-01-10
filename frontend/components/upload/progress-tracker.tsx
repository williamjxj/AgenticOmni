'use client';

import { useEffect, useState } from 'react';
import { CheckCircle2, Clock, AlertCircle, Loader2 } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Progress } from '@/components/ui/progress';
import { apiClient } from '@/lib/api/client';
import { JobStatus } from '@/lib/api/types';

interface ProgressTrackerProps {
  jobId: number;
  onComplete?: (status: JobStatus) => void;
}

export function ProgressTracker({ jobId, onComplete }: ProgressTrackerProps) {
  const [status, setStatus] = useState<JobStatus | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let interval: NodeJS.Timeout;

    const fetchStatus = async () => {
      try {
        const jobStatus = await apiClient.getJobStatus(jobId);
        setStatus(jobStatus);

        if (jobStatus.status === 'completed') {
          clearInterval(interval);
          onComplete?.(jobStatus);
        } else if (jobStatus.status === 'failed') {
          clearInterval(interval);
          setError(jobStatus.error_message || 'Processing failed');
        }
      } catch (err) {
        setError('Failed to fetch job status');
        clearInterval(interval);
      }
    };

    fetchStatus();
    interval = setInterval(fetchStatus, 2000); // Poll every 2 seconds

    return () => clearInterval(interval);
  }, [jobId, onComplete]);

  if (error) {
    return (
      <Card>
        <CardContent className="p-6">
          <div className="flex items-center gap-3 text-red-600">
            <AlertCircle className="h-5 w-5" />
            <span>{error}</span>
          </div>
        </CardContent>
      </Card>
    );
  }

  if (!status) {
    return (
      <Card>
        <CardContent className="p-6">
          <div className="flex items-center gap-3">
            <Loader2 className="h-5 w-5 animate-spin" />
            <span>Loading...</span>
          </div>
        </CardContent>
      </Card>
    );
  }

  const getStatusIcon = () => {
    switch (status.status) {
      case 'completed':
        return <CheckCircle2 className="h-5 w-5 text-green-600" />;
      case 'failed':
        return <AlertCircle className="h-5 w-5 text-red-600" />;
      case 'processing':
        return <Loader2 className="h-5 w-5 animate-spin text-blue-600" />;
      default:
        return <Clock className="h-5 w-5 text-slate-400" />;
    }
  };

  const getStatusColor = () => {
    switch (status.status) {
      case 'completed':
        return 'text-green-600';
      case 'failed':
        return 'text-red-600';
      case 'processing':
        return 'text-blue-600';
      default:
        return 'text-slate-600';
    }
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          {getStatusIcon()}
          Processing Status
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <div>
          <div className="flex justify-between text-sm mb-2">
            <span className="font-medium">Progress</span>
            <span className={getStatusColor()}>
              {status.progress_percent}%
            </span>
          </div>
          <Progress value={status.progress_percent} />
        </div>

        <div className="grid grid-cols-2 gap-4 text-sm">
          <div>
            <p className="text-slate-600 dark:text-slate-400">Job ID</p>
            <p className="font-medium">{status.job_id}</p>
          </div>
          <div>
            <p className="text-slate-600 dark:text-slate-400">Document ID</p>
            <p className="font-medium">{status.document_id}</p>
          </div>
          <div>
            <p className="text-slate-600 dark:text-slate-400">Status</p>
            <p className={`font-medium capitalize ${getStatusColor()}`}>
              {status.status}
            </p>
          </div>
          <div>
            <p className="text-slate-600 dark:text-slate-400">Type</p>
            <p className="font-medium">{status.job_type}</p>
          </div>
        </div>

        {status.status === 'completed' && (
          <div className="p-3 bg-green-50 dark:bg-green-950 rounded-md border border-green-200 dark:border-green-800">
            <p className="text-sm text-green-800 dark:text-green-200">
              ✓ Document processed successfully
            </p>
          </div>
        )}

        {status.error_message && (
          <div className="p-3 bg-red-50 dark:bg-red-950 rounded-md border border-red-200 dark:border-red-800">
            <p className="text-sm text-red-800 dark:text-red-200">
              {status.error_message}
            </p>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
