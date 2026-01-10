#!/usr/bin/env bash
# AgenticOmni Environment Validation Script
# Validates that all required environment variables are set

set -e

echo "======================================================================="
echo "AgenticOmni Environment Validation"
echo "======================================================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Track validation status
ERRORS=0
WARNINGS=0

# Function to check required variable
check_required() {
    local var_name=$1
    local var_value=${!var_name}
    
    if [ -z "$var_value" ]; then
        echo -e "${RED}✗${NC} $var_name is not set (REQUIRED)"
        ((ERRORS++))
    else
        echo -e "${GREEN}✓${NC} $var_name is set"
    fi
}

# Function to check optional variable
check_optional() {
    local var_name=$1
    local var_value=${!var_name}
    local default_value=$2
    
    if [ -z "$var_value" ]; then
        echo -e "${YELLOW}⚠${NC} $var_name is not set (using default: $default_value)"
        ((WARNINGS++))
    else
        echo -e "${GREEN}✓${NC} $var_name is set"
    fi
}

# Load .env file if it exists
if [ -f .env ]; then
    echo "Loading environment variables from .env file..."
    export $(grep -v '^#' .env | xargs)
    echo ""
else
    echo -e "${RED}✗${NC} .env file not found!"
    echo "   Please create .env file from .env.example"
    exit 1
fi

echo "Checking required environment variables..."
echo ""

# Database Configuration
echo "Database Configuration:"
check_required "DATABASE_URL"
check_optional "VECTOR_DIMENSIONS" "1536"

# API Configuration
echo ""
echo "API Configuration:"
check_optional "API_HOST" "0.0.0.0"
check_optional "API_PORT" "8000"
check_optional "API_VERSION" "v1"

# Security
echo ""
echo "Security:"
check_required "SECRET_KEY"

# Check SECRET_KEY length
if [ -n "$SECRET_KEY" ] && [ ${#SECRET_KEY} -lt 32 ]; then
    echo -e "${RED}✗${NC} SECRET_KEY must be at least 32 characters long"
    ((ERRORS++))
fi

# Logging
echo ""
echo "Logging:"
check_optional "LOG_LEVEL" "INFO"
check_optional "ENVIRONMENT" "development"

# CORS
echo ""
echo "CORS Configuration:"
check_optional "CORS_ORIGINS" "http://localhost:3000"

# LLM API Keys (optional but recommended)
echo ""
echo "LLM API Keys (optional):"
check_optional "OPENAI_API_KEY" "(not set)"
check_optional "ANTHROPIC_API_KEY" "(not set)"

# Redis
echo ""
echo "Redis Configuration:"
check_optional "REDIS_URL" "redis://localhost:6380/0"

# File Storage
echo ""
echo "File Storage:"
check_optional "UPLOAD_DIR" "./uploads"
check_optional "MAX_UPLOAD_SIZE_MB" "100"
check_optional "ALLOWED_FILE_TYPES" "pdf,docx,txt,png,jpg,jpeg"

# Summary
echo ""
echo "======================================================================="
echo "Validation Summary"
echo "======================================================================="

if [ $ERRORS -eq 0 ] && [ $WARNINGS -eq 0 ]; then
    echo -e "${GREEN}✓ All environment variables are properly configured!${NC}"
    exit 0
elif [ $ERRORS -eq 0 ]; then
    echo -e "${YELLOW}⚠ $WARNINGS warning(s) found (using defaults)${NC}"
    echo "   Your environment is functional but consider setting optional variables."
    exit 0
else
    echo -e "${RED}✗ $ERRORS error(s) found${NC}"
    if [ $WARNINGS -gt 0 ]; then
        echo -e "${YELLOW}⚠ $WARNINGS warning(s) found${NC}"
    fi
    echo ""
    echo "Please fix the errors above before proceeding."
    exit 1
fi
