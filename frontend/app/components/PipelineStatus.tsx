import React from 'react';

export default function PipelineStatus({ status }: { status: string }) {
  // Placeholder UI for pipeline status and logs
  return (
    <div>
      <h3>Pipeline Status</h3>
      <p>Status: {status}</p>
      {/* Add log display here */}
    </div>
  );
}
