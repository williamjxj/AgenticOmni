#!/usr/bin/env bash
# Quick Start - All Services for Markdown Upload → RAG → Search

set -e

echo "═══════════════════════════════════════════════════════════════════════"
echo "  AgenticOmni - Quick Start All Services"
echo "═══════════════════════════════════════════════════════════════════════"
echo ""

# Check if running in tmux or screen
if [ -z "$TMUX" ] && [ -z "$STY" ]; then
    echo "⚠️  This script works best in tmux or by running services manually"
    echo ""
    echo "Manual start (recommended):"
    echo ""
    echo "Terminal 1 - Backend:"
    echo "  cd /Users/william.jiang/my-apps/ai-edocuments"
    echo "  source venv/bin/activate"
    echo "  ./scripts/run_dev.sh"
    echo ""
    echo "Terminal 2 - Frontend:"
    echo "  cd /Users/william.jiang/my-apps/ai-edocuments/frontend"
    echo "  npm run dev"
    echo ""
    echo "Terminal 3 - Ollama (for embeddings):"
    echo "  ollama serve"
    echo ""
    echo "Then visit: http://localhost:3000/upload"
    echo ""
    exit 0
fi

# If in tmux, create windows
if [ -n "$TMUX" ]; then
    echo "🚀 Starting services in tmux windows..."
    
    # Backend
    tmux new-window -n "backend" "cd /Users/william.jiang/my-apps/ai-edocuments && source venv/bin/activate && ./scripts/run_dev.sh"
    
    # Frontend
    tmux new-window -n "frontend" "cd /Users/william.jiang/my-apps/ai-edocuments/frontend && npm run dev"
    
    # Ollama
    tmux new-window -n "ollama" "ollama serve"
    
    echo ""
    echo "✅ Services started in tmux windows!"
    echo ""
    echo "Switch between windows:"
    echo "  Ctrl+B, then W (window list)"
    echo "  Ctrl+B, then N (next window)"
    echo "  Ctrl+B, then P (previous window)"
    echo ""
fi

echo "═══════════════════════════════════════════════════════════════════════"
echo "  Services should now be running"
echo "═══════════════════════════════════════════════════════════════════════"
echo ""
echo "📍 Access Points:"
echo "  - Frontend:   http://localhost:3000"
echo "  - Upload:     http://localhost:3000/upload"
echo "  - Search:     http://localhost:3000/search"
echo "  - API Docs:   http://localhost:8000/api/v1/docs"
echo "  - Health:     http://localhost:8000/api/v1/health"
echo ""
echo "📖 Next Steps:"
echo "  1. Upload markdown files: http://localhost:3000/upload"
echo "  2. Generate embeddings: python scripts/generate_embeddings.py"
echo "  3. Search documents: http://localhost:3000/search"
echo ""
echo "💡 For detailed guide, see: docs/next-steps.md"
echo ""
