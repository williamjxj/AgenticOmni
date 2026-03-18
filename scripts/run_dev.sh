#!/usr/bin/env bash
# AgenticOmni Development Server Runner
# Starts the FastAPI server in development mode with hot-reload

set -e

echo "======================================================================="
echo "AgenticOmni Development Server"
echo "======================================================================="
echo ""

# Check if .env file exists
if [ ! -f .env ]; then
    echo "⚠️  Warning: .env file not found."
    echo "   Creating .env from .env.example..."
    cp .env.example .env
    echo "   ✅ Created .env file. Please configure your settings before proceeding."
    echo ""
fi

# Check if uvicorn is installed
if ! command -v uvicorn &> /dev/null; then
    echo "❌ Error: uvicorn not found. Install dependencies first:"
    echo "   pip install -e ."
    exit 1
fi

# Load environment variables
export $(grep -v '^#' .env | xargs)

echo "Starting FastAPI server..."
echo "  - Host: ${API_HOST:-0.0.0.0}"
echo "  - Port: ${API_PORT:-8000}"
echo "  - Environment: ${ENVIRONMENT:-development}"
echo "  - Log Level: ${LOG_LEVEL:-INFO}"
echo ""
echo "📚 API Documentation: http://localhost:${API_PORT:-8000}/api/v1/docs"
echo "🔍 ReDoc: http://localhost:${API_PORT:-8000}/api/v1/redoc"
echo ""
echo "Press Ctrl+C to stop the server"
echo "======================================================================="
echo ""

# Start server with hot-reload
uvicorn src.api.main:app \
    --host ${API_HOST:-0.0.0.0} \
    --port ${API_PORT:-8000} \
    --reload \
    --log-level $(echo "${LOG_LEVEL:-info}" | tr '[:upper:]' '[:lower:]')
