#!/usr/bin/env bash
# AgenticOmni Test Runner
# Runs pytest with coverage reporting

set -e

echo "======================================================================="
echo "AgenticOmni Test Suite"
echo "======================================================================="
echo ""

# Check if pytest is installed
if ! command -v pytest &> /dev/null; then
    echo "❌ Error: pytest not found. Install dev dependencies first:"
    echo "   pip install -e '.[dev]'"
    exit 1
fi

# Check if .env file exists
if [ ! -f .env ]; then
    echo "⚠️  Warning: .env file not found."
    echo "   Creating .env from .env.example..."
    cp .env.example .env
    echo ""
fi

# Export test database URL if not set
export DATABASE_URL="${TEST_DATABASE_URL:-postgresql+asyncpg://agenti_user:agenti_user@localhost:5436/agenticomni_test}"

echo "Running tests..."
echo "  - Test Database: ${DATABASE_URL}"
echo "  - Coverage Threshold: 80%"
echo ""
echo "======================================================================="
echo ""

# Run pytest with coverage
pytest \
    --cov=src \
    --cov-report=term-missing \
    --cov-report=html \
    --cov-report=xml \
    --cov-branch \
    --cov-fail-under=80 \
    -v \
    -ra \
    --tb=short \
    "$@"

EXIT_CODE=$?

echo ""
echo "======================================================================="

if [ $EXIT_CODE -eq 0 ]; then
    echo "✅ All tests passed!"
    echo ""
    echo "📊 Coverage report generated:"
    echo "   - HTML: htmlcov/index.html"
    echo "   - XML: coverage.xml"
else
    echo "❌ Tests failed with exit code: $EXIT_CODE"
fi

echo "======================================================================="

exit $EXIT_CODE
