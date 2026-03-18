import React from 'react';

export default function IngestionStatus({ jobId, status }: { jobId: number; status: string }) {
  // Placeholder UI for ingestion job status
  return (
    <div>
      <h3>Ingestion Job Status</h3>
      <p>Job ID: {jobId}</p>
      <p>Status: {status}</p>
    </div>
  );
}
