# Production Deployment Checklist

This document provides a comprehensive checklist for deploying AgenticOmni document processing pipeline to production.

## 📋 Pre-Deployment Checklist

### Infrastructure

- [ ] **PostgreSQL 14+** with pgvector extension installed
- [ ] **Redis 7+** for task queue (Dramatiq broker)
- [ ] **S3-compatible storage** (AWS S3, MinIO, etc.) configured
- [ ] **ClamAV daemon** running for malware scanning (optional but recommended)
- [ ] **Load balancer** configured (nginx, AWS ALB, etc.)
- [ ] **SSL/TLS certificates** installed
- [ ] **Monitoring system** (Prometheus, DataDog, etc.)
- [ ] **Log aggregation** (ELK, CloudWatch, etc.)

### Database

- [ ] Database migrations applied: `alembic upgrade head`
- [ ] Database indexes created (performance_indexes migration)
- [ ] Connection pooling configured (min 5, max 20 connections)
- [ ] Database backups scheduled (daily + WAL archiving)
- [ ] Row-level security policies applied for multi-tenancy
- [ ] Database credentials rotated and stored in secrets manager

### Storage

- [ ] S3 bucket created with appropriate IAM policies
- [ ] Bucket lifecycle policies configured (e.g., archive after 90 days)
- [ ] Bucket versioning enabled for disaster recovery
- [ ] CORS policies configured if needed for frontend uploads
- [ ] Storage quotas defined per tenant
- [ ] Backup strategy implemented for S3

### Security

- [ ] ClamAV malware scanning enabled (`ENABLE_MALWARE_SCANNING=true`)
- [ ] File upload size limits configured (`MAX_UPLOAD_SIZE_MB`)
- [ ] Allowed file types restricted (`ALLOWED_FILE_TYPES`)
- [ ] Rate limiting enabled on upload endpoints
- [ ] CORS headers properly configured
- [ ] API authentication implemented (JWT/OAuth2)
- [ ] Content Security Policy (CSP) headers added
- [ ] Input sanitization for filenames and metadata

### Environment Configuration

Required environment variables in `.env`:

```bash
# Database
DATABASE_URL=postgresql+asyncpg://user:pass@host:5432/agenticomni
DATABASE_POOL_SIZE=20
DATABASE_MAX_OVERFLOW=10

# Redis (Task Queue)
DRAMATIQ_BROKER_URL=redis://redis:6379/1
DRAMATIQ_RESULT_BACKEND=redis://redis:6379/2
MAX_CONCURRENT_PARSING_JOBS=10

# Storage
STORAGE_BACKEND=s3
S3_BUCKET_NAME=agenticomni-documents-prod
S3_REGION=us-east-1
S3_ACCESS_KEY_ID=<from-secrets-manager>
S3_SECRET_ACCESS_KEY=<from-secrets-manager>
S3_ENDPOINT_URL=https://s3.amazonaws.com

# Upload Configuration
MAX_UPLOAD_SIZE_MB=100
MAX_BATCH_SIZE=10
ALLOWED_FILE_TYPES=pdf,docx,txt

# Chunking
CHUNK_SIZE_TOKENS=512
CHUNK_OVERLAP_TOKENS=50
MIN_CHUNK_SIZE_TOKENS=100

# Security
ENABLE_MALWARE_SCANNING=true
CLAMAV_HOST=clamav.internal
CLAMAV_PORT=3310

# Monitoring
LOG_LEVEL=INFO
ENABLE_METRICS=true
SENTRY_DSN=<your-sentry-dsn>
```

## 🚀 Deployment Steps

### 1. Pre-Deployment Testing

```bash
# Run full test suite
pytest tests/ -v --cov=src

# Run type checking
mypy src/

# Run linting
ruff check src/

# Test database migrations on staging
alembic upgrade head

# Performance testing
pytest tests/integration/test_upload_api.py -k "performance" -v
```

### 2. Infrastructure Setup

#### PostgreSQL Setup

```sql
-- Create database
CREATE DATABASE agenticomni;

-- Install pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Create application user
CREATE USER agenticomni_app WITH PASSWORD '<strong-password>';
GRANT ALL PRIVILEGES ON DATABASE agenticomni TO agenticomni_app;
```

#### S3 Bucket Policy Example

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "AllowAppAccess",
      "Effect": "Allow",
      "Principal": {
        "AWS": "arn:aws:iam::ACCOUNT_ID:user/agenticomni-app"
      },
      "Action": [
        "s3:GetObject",
        "s3:PutObject",
        "s3:DeleteObject"
      ],
      "Resource": "arn:aws:s3:::agenticomni-documents-prod/*"
    }
  ]
}
```

#### ClamAV Setup (Docker)

```bash
# Start ClamAV daemon
docker run -d --name clamav \
  -p 3310:3310 \
  clamav/clamav:latest

# Wait for initial database download (can take 10-15 minutes)
docker logs -f clamav
```

### 3. Application Deployment

#### Using Docker Compose (Recommended)

```bash
# Build images
docker-compose -f docker-compose.prod.yml build

# Start services
docker-compose -f docker-compose.prod.yml up -d

# Run migrations
docker-compose -f docker-compose.prod.yml exec api alembic upgrade head

# Verify health
curl https://your-domain.com/api/v1/health
```

#### Using Kubernetes

```bash
# Apply Kubernetes manifests
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/secrets.yaml
kubectl apply -f k8s/configmap.yaml
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml
kubectl apply -f k8s/ingress.yaml

# Run migration job
kubectl apply -f k8s/migration-job.yaml

# Verify deployment
kubectl get pods -n agenticomni
kubectl logs -f deployment/api -n agenticomni
```

### 4. Post-Deployment Verification

#### Health Checks

```bash
# API health
curl https://api.your-domain.com/api/v1/health

# Database connectivity
curl https://api.your-domain.com/api/v1/health/db

# Redis connectivity
curl https://api.your-domain.com/api/v1/health/redis

# Storage connectivity
curl https://api.your-domain.com/api/v1/health/storage
```

#### Functional Testing

```bash
# Test single upload
curl -X POST "https://api.your-domain.com/api/v1/documents/upload" \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@test.pdf" \
  -F "tenant_id=1" \
  -F "user_id=1"

# Test batch upload
curl -X POST "https://api.your-domain.com/api/v1/documents/batch-upload" \
  -H "Authorization: Bearer $TOKEN" \
  -F "files=@doc1.pdf" \
  -F "files=@doc2.docx" \
  -F "tenant_id=1" \
  -F "user_id=1"

# Check processing status
curl "https://api.your-domain.com/api/v1/processing/jobs/1" \
  -H "Authorization: Bearer $TOKEN"
```

## 📊 Monitoring & Observability

### Key Metrics to Monitor

1. **Upload Metrics**
   - `upload_requests_total` (counter)
   - `upload_duration_seconds` (histogram)
   - `upload_size_bytes` (histogram)
   - `upload_errors_total` (counter by error_type)

2. **Processing Metrics**
   - `parsing_jobs_total` (counter by status)
   - `parsing_duration_seconds` (histogram)
   - `chunk_count` (histogram)
   - `parsing_errors_total` (counter by error_type)

3. **System Metrics**
   - Database connection pool usage
   - Redis queue depth
   - API response times (p50, p95, p99)
   - Storage usage per tenant
   - Memory and CPU usage

### Logging

Ensure structured JSON logs are captured for:
- All API requests (request ID, tenant ID, duration)
- Upload events (file size, MIME type, content hash)
- Processing events (job ID, progress, errors)
- Security events (malware detected, quota exceeded)

### Alerts

Set up alerts for:
- ❗ API error rate > 5% for 5 minutes
- ❗ Processing job failure rate > 10%
- ❗ Database connection pool exhausted
- ❗ Redis queue depth > 1000 jobs
- ⚠️ Storage quota > 90% for any tenant
- ⚠️ API response time p95 > 2 seconds
- ⚠️ Malware detected in uploads

## 🔒 Security Hardening

### API Security

- [ ] Implement rate limiting (e.g., 100 requests/minute per user)
- [ ] Add request size limits (max 100MB total per request)
- [ ] Validate Content-Type headers on all uploads
- [ ] Sanitize filenames (remove path traversal attempts)
- [ ] Implement CSRF protection for state-changing endpoints
- [ ] Add API key rotation mechanism
- [ ] Enable audit logging for sensitive operations

### Network Security

- [ ] Configure WAF rules (block SQL injection, XSS)
- [ ] Enable DDoS protection
- [ ] Use VPC/private subnets for internal services
- [ ] Restrict database access to application subnet only
- [ ] Enable encryption in transit (TLS 1.3)
- [ ] Enable encryption at rest (S3, RDS)

## 🔄 Maintenance

### Regular Tasks

**Daily:**
- Monitor error rates and alerts
- Check processing job queue depth
- Review security logs for anomalies

**Weekly:**
- Review storage usage and quotas
- Analyze slow query logs
- Update ClamAV virus definitions (automated)

**Monthly:**
- Review and rotate API keys
- Database vacuum and analyze
- Update dependencies and security patches
- Review and optimize database indexes

### Backup & Disaster Recovery

**Database Backups:**
- Automated daily snapshots (retain 30 days)
- WAL archiving for point-in-time recovery
- Test restore procedure monthly

**Storage Backups:**
- S3 versioning enabled
- Cross-region replication for critical data
- Test restore procedure quarterly

**Application Backups:**
- Container images tagged and stored in registry
- Configuration files backed up in version control
- Secrets backed up in encrypted storage

## 📈 Performance Optimization

### Database Optimization

```sql
-- Analyze query performance
EXPLAIN ANALYZE SELECT * FROM documents WHERE tenant_id = 1 ORDER BY created_at DESC LIMIT 20;

-- Update statistics
ANALYZE documents;
ANALYZE document_chunks;
ANALYZE processing_jobs;

-- Vacuum if needed
VACUUM ANALYZE documents;
```

### Application Optimization

- Enable database connection pooling
- Implement caching for frequently accessed data
- Use CDN for static assets
- Enable compression (gzip/brotli) on API responses
- Optimize chunk size for your use case (512 tokens default)

## 🚨 Rollback Procedure

If issues arise after deployment:

1. **Immediate rollback:**
   ```bash
   # Kubernetes
   kubectl rollout undo deployment/api -n agenticomni
   
   # Docker Compose
   docker-compose -f docker-compose.prod.yml down
   docker-compose -f docker-compose.prod.yml up -d --build --no-deps api
   ```

2. **Database rollback (if needed):**
   ```bash
   alembic downgrade -1  # Roll back one migration
   ```

3. **Verify rollback:**
   - Check health endpoints
   - Run smoke tests
   - Monitor error rates

## ✅ Production Launch Checklist

Final checks before going live:

- [ ] All automated tests passing
- [ ] Security scan completed (no critical vulnerabilities)
- [ ] Performance testing completed (meets SLA)
- [ ] Disaster recovery plan documented and tested
- [ ] Monitoring and alerts configured
- [ ] On-call rotation established
- [ ] Documentation complete and reviewed
- [ ] Stakeholder sign-off obtained

---

## 📞 Support Contacts

- **Infrastructure Issues**: ops-team@company.com
- **Application Issues**: dev-team@company.com
- **Security Incidents**: security@company.com
- **On-Call Rotation**: pagerduty.com/schedules/agenticomni

---

**Last Updated**: 2024-01-09  
**Next Review**: 2024-04-09
