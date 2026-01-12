#!/usr/bin/env bash
# AgenticOmni Database Reset Script
# Completely resets PostgreSQL and Redis for a fresh start

set -e

echo "======================================================================="
echo "AgenticOmni Database Reset"
echo "======================================================================="
echo ""
echo "⚠️  WARNING: This will delete ALL data from PostgreSQL and Redis!"
echo ""
read -p "Are you sure you want to continue? (yes/no): " -r
echo ""

if [[ ! $REPLY =~ ^[Yy][Ee][Ss]$ ]]; then
    echo "❌ Reset cancelled."
    exit 0
fi

echo "🔄 Starting database reset..."
echo ""

# Stop Docker services
echo "1️⃣  Stopping Docker services..."
docker-compose stop postgres redis
echo "   ✅ Services stopped"
echo ""

# Remove Docker volumes
echo "2️⃣  Removing PostgreSQL and Redis data volumes..."
docker volume rm agenticomni_postgres_data 2>/dev/null || echo "   ℹ️  PostgreSQL volume already removed or doesn't exist"
docker volume rm agenticomni_redis_data 2>/dev/null || echo "   ℹ️  Redis volume already removed or doesn't exist"
echo "   ✅ Volumes removed"
echo ""

# Start services again
echo "3️⃣  Starting Docker services with fresh volumes..."
docker-compose up -d postgres redis
echo "   ✅ Services started"
echo ""

# Wait for PostgreSQL to be healthy
echo "4️⃣  Waiting for PostgreSQL to be ready..."
for i in {1..30}; do
    if docker-compose exec -T postgres pg_isready -U agenti_user -d agenticomni > /dev/null 2>&1; then
        echo "   ✅ PostgreSQL is ready"
        break
    fi
    if [ $i -eq 30 ]; then
        echo "   ❌ PostgreSQL failed to start within 30 seconds"
        exit 1
    fi
    echo "   ⏳ Waiting... ($i/30)"
    sleep 1
done
echo ""

# Wait for Redis to be healthy
echo "5️⃣  Waiting for Redis to be ready..."
for i in {1..10}; do
    if docker-compose exec -T redis redis-cli ping > /dev/null 2>&1; then
        echo "   ✅ Redis is ready"
        break
    fi
    if [ $i -eq 10 ]; then
        echo "   ❌ Redis failed to start within 10 seconds"
        exit 1
    fi
    echo "   ⏳ Waiting... ($i/10)"
    sleep 1
done
echo ""

# Run Alembic migrations
echo "6️⃣  Running Alembic migrations to create schema..."
if command -v alembic &> /dev/null; then
    alembic upgrade head
    echo "   ✅ Database schema created"
else
    echo "   ❌ alembic not found. Please run: pip install -e ."
    exit 1
fi
echo ""

# Clear upload directories
echo "7️⃣  Clearing upload directories..."
rm -rf uploads/* tmp/* 2>/dev/null || true
mkdir -p uploads tmp
echo "   ✅ Upload directories cleared"
echo ""

echo "======================================================================="
echo "✅ Database Reset Complete!"
echo "======================================================================="
echo ""
echo "Services Status:"
echo "  - PostgreSQL: Running on port 5436"
echo "  - Redis: Running on port 6380"
echo ""
echo "Next Steps:"
echo "  1. Start the backend: ./scripts/run_dev.sh"
echo "  2. Start the frontend: cd frontend && npm run dev"
echo "  3. Upload documents: http://localhost:3000/upload"
echo ""
echo "Database is now fresh and ready for document upload and RAG!"
echo ""
