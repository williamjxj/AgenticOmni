import React from 'react';

export default function ExtractedDataViewer({ data }: { data: string[] }) {
  // Placeholder UI for viewing extracted data
  return (
    <div>
      <h3>Extracted Data</h3>
      <ul>
        {data.map((item, idx) => (
          <li key={idx}>{item}</li>
        ))}
      </ul>
    </div>
  );
}
