#!/usr/bin/env bash
# Quick test for document upload

echo "═══════════════════════════════════════════════════════════════════════"
echo "  Upload Test"
echo "═══════════════════════════════════════════════════════════════════════"
echo ""

# Check backend
echo "1️⃣  Checking backend..."
if curl -s http://localhost:8000/api/v1/health > /dev/null 2>&1; then
    echo "   ✅ Backend is running"
else
    echo "   ❌ Backend not running"
    echo ""
    echo "   Start backend with:"
    echo "   ./scripts/restart_backend.sh"
    echo ""
    exit 1
fi
echo ""

# Create test file
TEST_FILE="/tmp/test_upload_$(date +%s).md"
cat > "$TEST_FILE" << 'EOF'
# Test Document

This is a test markdown document.

## Section 1

Some content here.

## Section 2

More content here.
EOF

echo "2️⃣  Created test file: $TEST_FILE"
echo ""

# Upload
echo "3️⃣  Uploading document..."
RESPONSE=$(curl -s -w "\nHTTP_CODE:%{http_code}" -X POST "http://localhost:8000/api/v1/documents/upload" \
  -F "file=@$TEST_FILE" \
  -F "tenant_id=1" \
  -F "user_id=1")

HTTP_CODE=$(echo "$RESPONSE" | grep "HTTP_CODE:" | cut -d: -f2)
BODY=$(echo "$RESPONSE" | grep -v "HTTP_CODE:")

echo ""
echo "Response Code: $HTTP_CODE"
echo "Response Body:"
echo "$BODY" | jq '.' 2>/dev/null || echo "$BODY"
echo ""

# Cleanup
rm -f "$TEST_FILE"

if [ "$HTTP_CODE" = "201" ]; then
    DOC_ID=$(echo "$BODY" | jq -r '.document_id' 2>/dev/null)
    echo "═══════════════════════════════════════════════════════════════════════"
    echo "  ✅ Upload Successful!"
    echo "═══════════════════════════════════════════════════════════════════════"
    echo ""
    echo "Document ID: $DOC_ID"
    echo ""
    echo "Next steps:"
    echo "  1. Wait for parsing (5-10 seconds)"
    echo "  2. Generate embeddings: python scripts/generate_embeddings.py"
    echo "  3. Search: http://localhost:3000/search"
    echo ""
else
    echo "═══════════════════════════════════════════════════════════════════════"
    echo "  ❌ Upload Failed"
    echo "═══════════════════════════════════════════════════════════════════════"
    echo ""
    echo "Check backend logs for errors"
    echo ""
    exit 1
fi
