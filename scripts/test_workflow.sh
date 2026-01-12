#!/usr/bin/env bash
# Test the complete workflow: Upload → Parse → Embed → Search

set -e

echo "═══════════════════════════════════════════════════════════════════════"
echo "  AgenticOmni - Complete Workflow Test"
echo "═══════════════════════════════════════════════════════════════════════"
echo ""

# Check prerequisites
echo "1️⃣  Checking prerequisites..."

# Check if backend is running
if ! curl -s http://localhost:8000/api/v1/health > /dev/null 2>&1; then
    echo "❌ Backend not running. Start with: ./scripts/run_dev.sh"
    exit 1
fi
echo "   ✅ Backend is running"

# Check if Ollama is running
if ! curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
    echo "❌ Ollama not running. Start with: ollama serve"
    exit 1
fi
echo "   ✅ Ollama is running"

# Check if embedding model exists
if ! curl -s http://localhost:11434/api/tags | grep -q "nomic-embed-text"; then
    echo "⚠️  nomic-embed-text model not found. Pulling..."
    ollama pull nomic-embed-text:latest
fi
echo "   ✅ Embedding model ready"
echo ""

# Create test markdown file
echo "2️⃣  Creating test markdown file..."
TEST_FILE="test_upload_$(date +%s).md"
cat > "/tmp/$TEST_FILE" << 'EOF'
# Test Document for AgenticOmni

## Introduction

This is a test document to verify the complete workflow from upload to search.

## Features

AgenticOmni provides the following capabilities:

- Document upload and parsing
- RAG-optimized chunking
- Vector embeddings for semantic search
- Multi-format support (PDF, DOCX, TXT, Markdown)

## Conclusion

This document should be successfully uploaded, parsed, chunked, embedded, and searchable.
EOF
echo "   ✅ Test file created: /tmp/$TEST_FILE"
echo ""

# Upload document
echo "3️⃣  Uploading document..."
UPLOAD_RESPONSE=$(curl -s -X POST "http://localhost:8000/api/v1/documents/upload" \
  -H "X-Tenant-ID: 1" \
  -H "X-User-ID: 1" \
  -F "file=@/tmp/$TEST_FILE")

DOC_ID=$(echo "$UPLOAD_RESPONSE" | grep -o '"document_id":[0-9]*' | grep -o '[0-9]*')

if [ -z "$DOC_ID" ]; then
    echo "❌ Upload failed"
    echo "$UPLOAD_RESPONSE"
    exit 1
fi

echo "   ✅ Document uploaded (ID: $DOC_ID)"
echo ""

# Wait for parsing to complete
echo "4️⃣  Waiting for parsing to complete..."
sleep 5
echo "   ✅ Parsing complete"
echo ""

# Check chunks were created
echo "5️⃣  Verifying chunks were created..."
CHUNK_COUNT=$(docker-compose exec -T postgres psql -U agenti_user -d agenticomni -t -c \
  "SELECT COUNT(*) FROM document_chunks WHERE document_id = $DOC_ID;" | xargs)

if [ "$CHUNK_COUNT" -eq 0 ]; then
    echo "❌ No chunks created"
    exit 1
fi

echo "   ✅ Created $CHUNK_COUNT chunks"
echo ""

# Generate embeddings
echo "6️⃣  Generating embeddings..."
source venv/bin/activate
python scripts/generate_embeddings.py --tenant-id 1 > /dev/null 2>&1
echo "   ✅ Embeddings generated"
echo ""

# Verify embeddings
echo "7️⃣  Verifying embeddings..."
EMBEDDED_COUNT=$(docker-compose exec -T postgres psql -U agenti_user -d agenticomni -t -c \
  "SELECT COUNT(*) FROM document_chunks WHERE document_id = $DOC_ID AND embedding_vector IS NOT NULL;" | xargs)

if [ "$EMBEDDED_COUNT" -eq 0 ]; then
    echo "❌ No embeddings found"
    exit 1
fi

echo "   ✅ Embedded $EMBEDDED_COUNT/$CHUNK_COUNT chunks"
echo ""

# Test search
echo "8️⃣  Testing semantic search..."
SEARCH_RESPONSE=$(curl -s -X POST "http://localhost:8000/api/v1/search/semantic" \
  -H "Content-Type: application/json" \
  -d '{
    "query_text": "What are the features of AgenticOmni?",
    "tenant_id": 1,
    "top_k": 3
  }')

RESULT_COUNT=$(echo "$SEARCH_RESPONSE" | grep -o '"total_results":[0-9]*' | grep -o '[0-9]*')

if [ -z "$RESULT_COUNT" ] || [ "$RESULT_COUNT" -eq 0 ]; then
    echo "❌ Search returned no results"
    echo "$SEARCH_RESPONSE"
    exit 1
fi

echo "   ✅ Search returned $RESULT_COUNT results"
echo ""

# Cleanup
echo "9️⃣  Cleanup..."
rm -f "/tmp/$TEST_FILE"
echo "   ✅ Test file removed"
echo ""

echo "═══════════════════════════════════════════════════════════════════════"
echo "  ✅ Complete Workflow Test PASSED!"
echo "═══════════════════════════════════════════════════════════════════════"
echo ""
echo "Summary:"
echo "  - Document uploaded: ✓"
echo "  - Parsed and chunked: ✓ ($CHUNK_COUNT chunks)"
echo "  - Embeddings generated: ✓ ($EMBEDDED_COUNT embeddings)"
echo "  - Semantic search: ✓ ($RESULT_COUNT results)"
echo ""
echo "Next steps:"
echo "  1. Upload more documents: http://localhost:3000/upload"
echo "  2. Try search interface: http://localhost:3000/search"
echo "  3. Explore API: http://localhost:8000/api/v1/docs"
echo ""
