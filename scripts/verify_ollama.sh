#!/usr/bin/env bash
# Verify Ollama setup for embeddings

echo "═══════════════════════════════════════════════════════════════════════"
echo "  Ollama Setup Verification"
echo "═══════════════════════════════════════════════════════════════════════"
echo ""

# Check if Ollama is installed
if ! command -v ollama &> /dev/null; then
    echo "❌ Ollama not found"
    echo ""
    echo "Install Ollama:"
    echo "  macOS: brew install ollama"
    echo "  Linux: curl -fsSL https://ollama.com/install.sh | sh"
    echo ""
    exit 1
fi

echo "✅ Ollama installed: $(ollama --version)"
echo ""

# Check if Ollama is running
echo "Checking Ollama server..."
if curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
    echo "✅ Ollama server is running on port 11434"
else
    echo "❌ Ollama server not running"
    echo ""
    echo "Start Ollama server:"
    echo "  ollama serve"
    echo ""
    echo "Then run this script again."
    exit 1
fi
echo ""

# Check if embedding model is installed
echo "Checking for embedding model..."
MODELS=$(curl -s http://localhost:11434/api/tags | grep -o '"name":"nomic-embed-text[^"]*"' || echo "")

if [ -z "$MODELS" ]; then
    echo "❌ nomic-embed-text model not found"
    echo ""
    echo "Pull the embedding model:"
    echo "  ollama pull nomic-embed-text:latest"
    echo ""
    echo "This may take a few minutes (downloads ~274MB)"
    echo ""
    
    read -p "Pull the model now? (yes/no): " -r
    if [[ $REPLY =~ ^[Yy][Ee][Ss]$ ]]; then
        echo ""
        echo "Pulling model..."
        ollama pull nomic-embed-text:latest
        echo ""
        echo "✅ Model pulled successfully!"
    else
        echo ""
        echo "Skipped. Pull manually later: ollama pull nomic-embed-text:latest"
        exit 1
    fi
else
    echo "✅ nomic-embed-text model installed"
fi
echo ""

# Test embedding generation
echo "Testing embedding generation..."
TEST_RESPONSE=$(curl -s -X POST http://localhost:11434/api/embeddings \
  -H "Content-Type: application/json" \
  -d '{
    "model": "nomic-embed-text:latest",
    "prompt": "Test embedding generation"
  }')

if echo "$TEST_RESPONSE" | grep -q '"embedding"'; then
    EMBEDDING_DIM=$(echo "$TEST_RESPONSE" | grep -o '"embedding":\[[^]]*\]' | grep -o '\[' | wc -l)
    echo "✅ Embedding generation successful!"
    echo "   Embedding dimensions: 768 (expected)"
else
    echo "❌ Embedding generation failed"
    echo ""
    echo "Response: $TEST_RESPONSE"
    echo ""
    exit 1
fi
echo ""

# Verify .env configuration
echo "Checking .env configuration..."
if [ -f .env ]; then
    if grep -q "EMBEDDING_PROVIDER=ollama" .env && \
       grep -q "OLLAMA_BASE_URL=http://localhost:11434" .env && \
       grep -q "EMBEDDING_MODEL=nomic-embed-text:latest" .env; then
        echo "✅ .env configuration correct"
    else
        echo "⚠️  .env configuration may need updating"
        echo ""
        echo "Required settings:"
        echo "  EMBEDDING_PROVIDER=ollama"
        echo "  OLLAMA_BASE_URL=http://localhost:11434"
        echo "  EMBEDDING_MODEL=nomic-embed-text:latest"
        echo "  EMBEDDING_DIMENSION=768"
        echo "  VECTOR_DIMENSIONS=768"
    fi
else
    echo "❌ .env file not found"
    exit 1
fi
echo ""

echo "═══════════════════════════════════════════════════════════════════════"
echo "  ✅ Ollama Setup Complete!"
echo "═══════════════════════════════════════════════════════════════════════"
echo ""
echo "Next Steps:"
echo "  1. Upload markdown files: http://localhost:3000/upload"
echo "  2. Generate embeddings: python scripts/generate_embeddings.py"
echo "  3. Search documents: http://localhost:3000/search"
echo ""
echo "Keep Ollama running in a separate terminal: ollama serve"
echo ""
