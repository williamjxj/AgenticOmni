import React from 'react';

export default function AuditTrail({ entries }: { entries: { action: string; timestamp: string; details: string }[] }) {
  // Placeholder UI for audit trail
  return (
    <div>
      <h3>Audit Trail</h3>
      <ul>
        {entries.map((entry, idx) => (
          <li key={idx}>
            <strong>{entry.action}</strong> at {entry.timestamp}: {entry.details}
          </li>
        ))}
      </ul>
    </div>
  );
}
