# Environment Configuration Guide

This document provides a comprehensive guide to all environment variables used in AgenticOmni.

## Quick Setup

Copy this template to your `.env` file in the project root:

```bash
cp docs/ENV_CONFIGURATION.md .env
# Then edit .env with your actual values
```

---

## Environment Variables Template

```bash
# ============================================================================
# Database Configuration (Required)
# ============================================================================
DATABASE_URL=postgresql+asyncpg://agenticomni:password@localhost:5436/agenticomni
DATABASE_POOL_SIZE=10
DATABASE_MAX_OVERFLOW=20

# ============================================================================
# Security (Required)
# ============================================================================
SECRET_KEY=your-secret-key-min-32-characters-long-change-this-in-production
ENFORCE_TENANT_ISOLATION=true

# ============================================================================
# API Server
# ============================================================================
API_HOST=0.0.0.0
API_PORT=8000
CORS_ORIGINS=http://localhost:3000,http://localhost:3001
API_VERSION=v1

# ============================================================================
# Environment
# ============================================================================
ENVIRONMENT=development
DEBUG=false
LOG_LEVEL=INFO
LOG_FORMAT=json

# ============================================================================
# Redis
# ============================================================================
REDIS_URL=redis://localhost:6379/0
REDIS_MAX_CONNECTIONS=10

# ============================================================================
# Document Upload & Storage
# ============================================================================
STORAGE_BACKEND=local
UPLOAD_DIR=./uploads
TEMP_UPLOAD_DIR=./tmp/uploads
MAX_UPLOAD_SIZE_MB=50
MAX_BATCH_SIZE=10
ALLOWED_FILE_TYPES=pdf,docx,txt

# ============================================================================
# Task Queue (Dramatiq)
# ============================================================================
DRAMATIQ_BROKER_URL=redis://localhost:6379/1
DRAMATIQ_RESULT_BACKEND=redis://localhost:6379/1
MAX_CONCURRENT_PARSING_JOBS=5
PARSING_TIMEOUT_SECONDS=300

# ============================================================================
# Document Chunking for RAG
# ============================================================================
CHUNK_SIZE_TOKENS=512
CHUNK_OVERLAP_TOKENS=50
MIN_CHUNK_SIZE_TOKENS=100

# ============================================================================
# Vector Store
# ============================================================================
VECTOR_DIMENSIONS=1536

# ============================================================================
# S3 Storage (Optional - for production)
# ============================================================================
# S3_BUCKET=agenticomni-documents
# S3_REGION=us-east-1
# AWS_ACCESS_KEY_ID=your-access-key
# AWS_SECRET_ACCESS_KEY=your-secret-key

# ============================================================================
# Malware Scanning (Optional)
# ============================================================================
ENABLE_MALWARE_SCANNING=false
CLAMAV_HOST=localhost
CLAMAV_PORT=3310

# ============================================================================
# LLM Configuration - DeepSeek (Primary Provider)
# ============================================================================
LLM_PROVIDER=deepseek

# DeepSeek API Configuration
DEEPSEEK_API_KEY=your-deepseek-api-key-here
DEEPSEEK_API_BASE=https://api.deepseek.com/v1
DEEPSEEK_MODEL=deepseek-chat
DEEPSEEK_TEMPERATURE=0.7
DEEPSEEK_MAX_TOKENS=4096

# ============================================================================
# Alternative LLM Providers (Optional)
# ============================================================================
# OpenAI Configuration (if LLM_PROVIDER=openai)
# OPENAI_API_KEY=your-openai-api-key-here

# Anthropic Configuration (if LLM_PROVIDER=anthropic)
# ANTHROPIC_API_KEY=your-anthropic-api-key-here

# ============================================================================
# Embedding Configuration
# ============================================================================
EMBEDDING_PROVIDER=openai
EMBEDDING_MODEL=text-embedding-3-small
EMBEDDING_DIMENSION=1536

# ============================================================================
# RAG Configuration
# ============================================================================
RAG_ENABLED=true
RAG_TEMPERATURE=0.3
RAG_TOP_K=5
RAG_CONTEXT_WINDOW=8000
RAG_SIMILARITY_THRESHOLD=0.7
```

---

## Configuration Details

### DeepSeek LLM Setup

1. **Get API Key**: Sign up at [https://platform.deepseek.com](https://platform.deepseek.com)
2. **Add to .env**:
   ```bash
   DEEPSEEK_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxx
   ```
3. **Select Model**:
   - `deepseek-chat` - General purpose chat (default)
   - `deepseek-coder` - Optimized for code generation

### Model Comparison

| Provider | Model | Context Window | Cost | Best For |
|----------|-------|----------------|------|----------|
| **DeepSeek** | deepseek-chat | 32K tokens | Low | General RAG, Cost-effective |
| **DeepSeek** | deepseek-coder | 16K tokens | Low | Code documentation |
| **OpenAI** | gpt-4-turbo | 128K tokens | High | Complex reasoning |
| **OpenAI** | gpt-3.5-turbo | 16K tokens | Medium | Fast responses |

### Environment-Specific Configurations

#### Development

```bash
ENVIRONMENT=development
DEBUG=true
LOG_LEVEL=DEBUG
LOG_FORMAT=console
STORAGE_BACKEND=local
ENABLE_MALWARE_SCANNING=false
```

#### Staging

```bash
ENVIRONMENT=staging
DEBUG=false
LOG_LEVEL=INFO
LOG_FORMAT=json
STORAGE_BACKEND=s3
ENABLE_MALWARE_SCANNING=true
```

#### Production

```bash
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=WARNING
LOG_FORMAT=json
STORAGE_BACKEND=s3
ENABLE_MALWARE_SCANNING=true
MAX_CONCURRENT_PARSING_JOBS=20
DATABASE_POOL_SIZE=20
```

---

## Configuration Validation

Validate your configuration:

```bash
# Check settings load correctly
python -c "from src.shared.config import settings; print(settings.model_dump_json(indent=2))"

# Test database connection
python -c "from src.storage_indexing.database import engine; import asyncio; asyncio.run(engine.connect())"

# Test LLM connection
python scripts/test_llm.py
```

---

## Security Best Practices

### ✅ DO:
- Use strong, unique SECRET_KEY (min 32 characters)
- Rotate API keys regularly
- Use environment-specific configurations
- Enable ENFORCE_TENANT_ISOLATION in production
- Store secrets in secrets manager (AWS Secrets Manager, HashiCorp Vault)

### ❌ DON'T:
- Commit .env files to version control
- Share API keys in documentation/tickets
- Use default passwords in production
- Disable tenant isolation in production

---

## Troubleshooting

### Common Issues

**Issue**: `ValidationError: DATABASE_URL field required`
**Solution**: Ensure DATABASE_URL is set in .env file

**Issue**: `DeepSeek API authentication failed`
**Solution**: Verify DEEPSEEK_API_KEY is correct and has credits

**Issue**: `Vector dimension mismatch`
**Solution**: Ensure VECTOR_DIMENSIONS matches EMBEDDING_DIMENSION

**Issue**: `Redis connection refused`
**Solution**: Start Redis: `docker-compose up -d redis`

---

## Environment Variable Priority

1. Operating system environment variables
2. `.env` file in project root
3. Default values in `config/settings.py`

---

## Testing Configuration

Create a `.env.test` for testing:

```bash
DATABASE_URL=postgresql+asyncpg://test:test@localhost:5436/test_db
STORAGE_BACKEND=local
UPLOAD_DIR=./test_uploads
ENABLE_MALWARE_SCANNING=false
LLM_PROVIDER=deepseek
DEEPSEEK_API_KEY=test-key
```

Load test environment:

```bash
export ENV_FILE=.env.test
pytest tests/
```

---

## DeepSeek-Specific Configuration

### Rate Limits

DeepSeek has the following rate limits:
- **Free Tier**: 60 requests/minute
- **Paid Tier**: 3000 requests/minute

Configure rate limiting in your application:

```bash
# Add these to .env if using rate limiting
DEEPSEEK_RPM_LIMIT=60
DEEPSEEK_RETRY_ATTEMPTS=3
DEEPSEEK_RETRY_DELAY=1
```

### Model Parameters

Fine-tune DeepSeek responses:

```bash
# For more creative responses
DEEPSEEK_TEMPERATURE=0.9
DEEPSEEK_MAX_TOKENS=8000

# For more deterministic/factual responses (RAG queries)
RAG_TEMPERATURE=0.1
DEEPSEEK_TEMPERATURE=0.3
```

### Cost Optimization

```bash
# Use smaller context window to reduce costs
RAG_CONTEXT_WINDOW=4000
DEEPSEEK_MAX_TOKENS=2048

# Retrieve fewer chunks
RAG_TOP_K=3

# Use higher similarity threshold to get only relevant chunks
RAG_SIMILARITY_THRESHOLD=0.8
```

---

## References

- [DeepSeek Platform](https://platform.deepseek.com)
- [DeepSeek API Documentation](https://platform.deepseek.com/api-docs)
- [Pydantic Settings Documentation](https://docs.pydantic.dev/latest/concepts/pydantic_settings/)

---

**Last Updated**: 2026-01-09  
**Version**: 0.2.0
