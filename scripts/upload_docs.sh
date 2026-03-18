#!/bin/bash
for file in docs/*.md; do
    echo "Uploading $file..."
    curl -s -X POST "http://localhost:8000/api/v1/documents/upload" \
      -F "file=@$file" \
      -F "tenant_id=1" \
      -F "user_id=1" | jq '.document_id, .filename'
    sleep 1
done
