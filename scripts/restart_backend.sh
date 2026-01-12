#!/usr/bin/env bash
# Restart backend with clean cache

echo "═══════════════════════════════════════════════════════════════════════"
echo "  Restarting Backend Server"
echo "═══════════════════════════════════════════════════════════════════════"
echo ""

# Stop any running backend
echo "1️⃣  Stopping existing backend processes..."
pkill -f "uvicorn src.api.main:app" || echo "   No running processes found"
sleep 2
echo "   ✅ Processes stopped"
echo ""

# Clear Python cache
echo "2️⃣  Clearing Python cache..."
cd /Users/william.jiang/my-apps/ai-edocuments
find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null
find . -name "*.pyc" -delete 2>/dev/null
echo "   ✅ Cache cleared"
echo ""

# Activate virtual environment
echo "3️⃣  Activating virtual environment..."
source venv/bin/activate
echo "   ✅ Virtual environment activated"
echo ""

# Check database connection
echo "4️⃣  Checking database connection..."
if docker-compose exec -T postgres pg_isready -U agenti_user -d agenticomni > /dev/null 2>&1; then
    echo "   ✅ Database is ready"
else
    echo "   ❌ Database not ready. Start with: docker-compose up -d postgres redis"
    exit 1
fi
echo ""

# Start backend
echo "5️⃣  Starting backend server..."
echo ""
echo "═══════════════════════════════════════════════════════════════════════"
echo "  Backend server starting..."
echo "  - URL: http://localhost:8000"
echo "  - API Docs: http://localhost:8000/api/v1/docs"
echo "  - Health: http://localhost:8000/api/v1/health"
echo ""
echo "  Press Ctrl+C to stop"
echo "═══════════════════════════════════════════════════════════════════════"
echo ""

# Run uvicorn
uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000
