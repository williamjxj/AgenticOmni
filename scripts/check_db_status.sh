#!/usr/bin/env bash
# Quick Database Status Check

echo "======================================================================="
echo "AgenticOmni Database Status"
echo "======================================================================="
echo ""

# Check Docker services
echo "🐳 Docker Services:"
docker-compose ps --format "table {{.Service}}\t{{.Status}}\t{{.Ports}}" 2>/dev/null | grep -E "(SERVICE|postgres|redis)" || echo "  ❌ Docker Compose not running"
echo ""

# Check PostgreSQL
echo "🗄️  PostgreSQL Data:"
docker-compose exec -T postgres psql -U agenti_user -d agenticomni -c "
SELECT 
    'Documents' as table_name, COUNT(*) as count FROM documents
UNION ALL
SELECT 'Chunks', COUNT(*) FROM document_chunks
UNION ALL
SELECT 'Jobs', COUNT(*) FROM processing_jobs
UNION ALL
SELECT 'Markdown Metadata', COUNT(*) FROM markdown_metadata
UNION ALL
SELECT 'Extracted Texts', COUNT(*) FROM extracted_texts
ORDER BY table_name;
" 2>/dev/null || echo "  ❌ PostgreSQL connection failed"
echo ""

# Check Redis
echo "🔴 Redis Keys:"
REDIS_KEYS=$(docker-compose exec -T redis redis-cli DBSIZE 2>/dev/null | tail -1)
echo "  Total Keys: $REDIS_KEYS"
echo ""

# Check Upload Directories
echo "📁 Upload Directories:"
UPLOAD_COUNT=$(find uploads -type f 2>/dev/null | wc -l | xargs)
TMP_COUNT=$(find tmp -type f 2>/dev/null | wc -l | xargs)
echo "  uploads/: $UPLOAD_COUNT files"
echo "  tmp/: $TMP_COUNT files"
echo ""

echo "======================================================================="
