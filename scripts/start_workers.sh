#!/bin/bash

# Start Dramatiq workers for processing tasks
# This script starts the background workers that process documents

set -e

echo "════════════════════════════════════════════════════════════════════════"
echo "  Starting Dramatiq Workers"
echo "════════════════════════════════════════════════════════════════════════"
echo ""

cd "$(dirname "$0")/.."

# Check if Redis is running
if ! curl -s http://localhost:8000/api/v1/health > /dev/null 2>&1; then
    echo "⚠️  Backend API not running. Start it first with: uvicorn src.api.main:app --reload"
    exit 1
fi

echo "1️⃣  Activating virtual environment..."
if [ -d ".venv" ]; then
    source .venv/bin/activate
    echo "   ✅ Virtual environment activated"
else
    echo "   ⚠️  No virtual environment found at .venv"
fi
echo ""

echo "2️⃣  Starting Dramatiq workers..."
echo "   - Processing parsing, chunking, and embedding tasks"
echo "   - Workers: 4 threads"
echo "   - Queue: default"
echo ""

# Start workers in the foreground
# Include both document_tasks and embedding_tasks modules
dramatiq src.ingestion_parsing.tasks.document_tasks src.ingestion_parsing.tasks.embedding_tasks \
    --processes 1 \
    --threads 4 \
    --verbose

echo ""
echo "════════════════════════════════════════════════════════════════════════"
echo "  Workers Started"
echo "════════════════════════════════════════════════════════════════════════"
