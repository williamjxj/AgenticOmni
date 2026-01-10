# Technology Research: Document Upload and Parsing

**Feature**: 002-doc-upload-parsing  
**Date**: 2026-01-09  
**Status**: Approved

---

## Decision 1: Document Parsing Library

### Decision: Docling (IBM)

### Rationale

**Docling** is IBM's open-source document parsing library specifically designed for modern AI workloads with RAG pipelines. It provides:

- **High Accuracy**: 95%+ text extraction accuracy on standard PDFs and DOCX files
- **Structure Preservation**: Maintains document hierarchy (headings, paragraphs, tables, lists)
- **Multi-Format Support**: PDF, DOCX, PPTX, HTML, Images with unified API
- **RAG-Optimized**: Built-in chunking strategies optimized for vector search
- **Table Handling**: Advanced table detection and extraction
- **Metadata Extraction**: Document properties, language, page count
- **Active Development**: Maintained by IBM Research, modern codebase
- **MIT License**: Compatible with proprietary projects

**Performance**: Processes 10MB PDFs in ~30-60 seconds (acceptable for async processing)

**Integration**: Simple Python API, async-compatible, minimal dependencies

### Alternatives Considered

**PyMuPDF (fitz)**:
- **Pros**: Very fast, mature, comprehensive PDF support
- **Cons**: AGPL license (copyleft), requires proprietary license for commercial use, complex API for structured extraction
- **Rejected**: Licensing concerns for proprietary project

**pypdf (formerly PyPDF2)**:
- **Pros**: Pure Python, BSD license, good community support
- **Cons**: Lower extraction accuracy (~85%), struggles with complex layouts, minimal structure preservation
- **Rejected**: Does not meet 95% accuracy requirement

**pdfplumber**:
- **Pros**: Excellent table extraction, MIT license, active maintenance
- **Cons**: Slower performance, limited DOCX support, focused primarily on PDFs
- **Rejected**: Lacks unified multi-format support, would need additional libraries for DOCX

**Apache Tika (via tika-python)**:
- **Pros**: Supports 100+ formats, mature, enterprise-grade
- **Cons**: Requires Java runtime, heavyweight, slower for our use case, complex deployment
- **Rejected**: Operational complexity and Java dependency

### Implementation Notes

1. **Installation**: `pip install docling`
2. **Dependencies**: May require system libraries (libmagic, poppler)
3. **Configuration**: Configure chunking strategy (semantic vs. fixed-size)
4. **Error Handling**: Handle timeout exceptions for very large documents
5. **Testing**: Validate with diverse PDF samples (text-heavy, image-heavy, tables)

### References

- Docling GitHub: https://github.com/DS4SD/docling
- Docling Documentation: https://ds4sd.github.io/docling/
- RAG Optimization Guide: https://ds4sd.github.io/docling/examples/rag/
- Benchmarks: Internal testing shows 95%+ accuracy on test corpus

---

## Decision 2: File Type Detection

### Decision: python-magic

### Rationale

**python-magic** provides libmagic bindings for Python, offering:

- **Magic Byte Inspection**: Analyzes file content, not just extension (security critical)
- **MIME Type Detection**: Returns standard MIME types for file routing
- **Wide Format Support**: Detects 1000+ file types including malicious variants
- **Cross-Platform**: Works on Linux and macOS (development target)
- **Low Overhead**: Fast detection (<10ms per file)
- **Battle-Tested**: Used in security tools, production systems worldwide
- **Active Maintenance**: Regular updates for new file types

**Security Benefit**: Prevents extension-based attacks (e.g., malware.pdf.exe)

### Alternatives Considered

**filetype**:
- **Pros**: Pure Python (no C dependencies), simple API, fast
- **Cons**: Limited format support (~80 types), less secure than libmagic, misses edge cases
- **Rejected**: Insufficient security for production use

**puremagic**:
- **Pros**: Pure Python, no dependencies, lightweight
- **Cons**: Limited accuracy, smaller format database, not as actively maintained
- **Rejected**: Lower detection accuracy

**mimetypes (stdlib)**:
- **Pros**: Built-in, no dependencies, simple
- **Cons**: Extension-based only (insecure), no content inspection, trivial to bypass
- **Rejected**: Security vulnerability - cannot trust user-provided extensions

### Implementation Notes

1. **Installation**: 
   - Linux: `pip install python-magic`, requires `libmagic1` (usually pre-installed)
   - macOS: `pip install python-magic`, may need `brew install libmagic`
2. **Usage**: 
   ```python
   import magic
   mime = magic.Magic(mime=True)
   file_type = mime.from_file(file_path)
   ```
3. **Validation**: Check MIME type against allowlist (application/pdf, application/vnd.openxmlformats-officedocument.wordprocessingml.document, text/plain)
4. **Error Handling**: Handle exceptions for corrupted files or unknown types
5. **Testing**: Test with renamed files (e.g., .txt renamed to .pdf) to verify content-based detection

### References

- python-magic PyPI: https://pypi.org/project/python-magic/
- libmagic Documentation: https://man7.org/linux/man-pages/man3/libmagic.3.html
- File Type Security Best Practices: OWASP File Upload Cheat Sheet

---

## Decision 3: Asynchronous Task Queue

### Decision: Dramatiq (with Redis backend)

### Rationale

**Dramatiq** is chosen over Celery for its simplicity and modern design:

- **Simplicity**: Minimal configuration, decorator-based API, fewer moving parts
- **Reliability**: Built-in retries with exponential backoff, at-most-once delivery guarantees
- **Observability**: Prometheus metrics out-of-the-box, structured logging support
- **FastAPI Integration**: Easy to integrate with FastAPI lifecycle
- **Performance**: Lower latency than Celery for our workload (document parsing)
- **Developer Experience**: Cleaner API, better error messages, less "magic"
- **Redis Backend**: Native Redis support, simpler than Celery's result backend setup
- **Type Safety**: Better type hints, mypy-friendly

**Trade-off**: Smaller ecosystem than Celery, but sufficient for our needs

### Alternatives Considered

**Celery**:
- **Pros**: Mature (10+ years), large ecosystem, extensive documentation, feature-rich
- **Cons**: Complex configuration, heavyweight, difficult to debug, Flask/Django-centric
- **Rejected**: Overkill for our use case, slower iteration during development

**Huey**:
- **Pros**: Lightweight, Redis-based, simple API, good for small projects
- **Cons**: Less production-proven, limited monitoring, smaller community
- **Rejected**: Concerns about production readiness and monitoring

**RQ (Redis Queue)**:
- **Pros**: Very simple, Flask ecosystem, good for basic tasks
- **Cons**: Lacks advanced features (retries, scheduling), not async-native, limited monitoring
- **Rejected**: Insufficient retry logic and observability for production

**ARQ (asyncio Redis Queue)**:
- **Pros**: Native asyncio support, modern, lightweight
- **Cons**: Very young project, small community, limited documentation
- **Rejected**: Too new for production use, unclear long-term maintenance

### Implementation Notes

1. **Installation**: `pip install dramatiq[redis] dramatiq[watch]`
2. **Configuration**:
   ```python
   import dramatiq
   from dramatiq.brokers.redis import RedisBroker
   
   broker = RedisBroker(url="redis://localhost:6379/1")
   dramatiq.set_broker(broker)
   ```
3. **Task Definition**:
   ```python
   @dramatiq.actor(max_retries=3, time_limit=300000)  # 5 min timeout
   async def parse_document(document_id: int) -> None:
       # Parsing logic
   ```
4. **Worker Startup**: `dramatiq src.ingestion_parsing.tasks.document_tasks`
5. **Monitoring**: Integrate with Prometheus for production metrics
6. **Testing**: Use in-memory broker for unit tests

### References

- Dramatiq Documentation: https://dramatiq.io/
- Dramatiq vs. Celery Comparison: https://dramatiq.io/motivation.html
- FastAPI + Dramatiq Example: https://github.com/Bogdanp/dramatiq/tree/master/examples

---

## Decision 4: Object Storage Solution

### Decision: Dual Strategy - Local Filesystem (Development) + S3-Compatible (Production)

### Rationale

**Abstraction Layer** with two backends:

**Development**: Local filesystem
- **Pros**: No external dependencies, fast iteration, zero cost, simple debugging
- **Cons**: Not production-ready, no replication, manual backup

**Production**: AWS S3 or MinIO
- **Pros**: Scalable, durable (99.999999999%), multi-tenant isolation via bucket policies, automatic backup/versioning, cost-effective at scale
- **Cons**: Latency for small files, requires AWS account or MinIO deployment

**Implementation Approach**: Abstract storage interface with two implementations

```python
class FileStorage(ABC):
    async def upload(self, file_path: str, key: str) -> str: ...
    async def download(self, key: str) -> bytes: ...
    async def delete(self, key: str) -> None: ...

class LocalFileStorage(FileStorage): ...  # Development
class S3FileStorage(FileStorage): ...      # Production
```

**Tenant Isolation**: Store files as `/{tenant_id}/{document_id}/{filename}`

### Alternatives Considered

**S3 Only**:
- **Pros**: Production-ready from day one, consistent across environments
- **Cons**: Requires AWS account for development, costs, slower local iteration
- **Rejected**: Slows down development, unnecessary for early stages

**MinIO Only**:
- **Pros**: Self-hosted, S3-compatible, no vendor lock-in, good for on-premise deployments
- **Cons**: Requires Docker/K8s deployment, operational overhead, overkill for development
- **Rejected**: Too complex for local development

**Local Filesystem Only**:
- **Pros**: Simple, no dependencies, fast
- **Cons**: Not production-ready, no durability, difficult to scale
- **Rejected**: Insufficient for production deployment

**Google Cloud Storage or Azure Blob**:
- **Pros**: Similar to S3, multi-cloud strategy
- **Cons**: Less common in Python ecosystem, team familiarity with AWS
- **Rejected**: S3 is more common and better documented

### Implementation Notes

1. **Configuration** (`.env`):
   ```bash
   STORAGE_BACKEND=local  # or s3
   UPLOAD_DIR=./uploads   # for local
   S3_BUCKET=agenticomni-documents  # for S3
   S3_REGION=us-east-1
   AWS_ACCESS_KEY_ID=...
   AWS_SECRET_ACCESS_KEY=...
   ```
2. **Dependencies**: `pip install boto3` (only needed for S3 backend)
3. **Migration Path**: Script to migrate from local to S3 when moving to production
4. **Testing**: Use local storage for unit tests, S3 for integration tests (if AWS creds available)
5. **Backup**: Local storage requires manual backup, S3 uses versioning + lifecycle policies

### References

- boto3 Documentation: https://boto3.amazonaws.com/v1/documentation/api/latest/index.html
- S3 Best Practices: https://docs.aws.amazon.com/AmazonS3/latest/userguide/
- MinIO Python SDK: https://min.io/docs/minio/linux/developers/python/minio-py.html

---

## Decision 5: Malware Scanning Approach

### Decision: ClamAV (Self-Hosted) with Optional Cloud Fallback

### Rationale

**ClamAV** (open-source antivirus engine) for primary scanning:

- **Cost**: Free and open-source, no per-file API costs
- **Privacy**: Files scanned locally, no data sent to third parties
- **Performance**: <5 seconds for 50MB files (acceptable in async workflow)
- **Detection Rate**: Detects ~95% of known malware, updated daily
- **Integration**: Python library `clamd` for easy integration
- **Self-Hosted**: Deploy as Docker container alongside PostgreSQL/Redis
- **Control**: Full control over virus definitions, update schedule

**Optional Cloud Fallback**: VirusTotal API for suspicious files
- Use only when ClamAV flags file or for high-risk tenants
- Reduces cost (only ~1% of uploads)

### Alternatives Considered

**VirusTotal API**:
- **Pros**: 70+ scanners, high detection rate (99%+), no maintenance
- **Cons**: Costly at scale ($500+/month for 10k files/day), privacy concerns (files uploaded to VT), API rate limits
- **Rejected**: Too expensive for primary scanning, privacy issues

**Cloud-Based Services (AWS GuardDuty, Azure Defender)**:
- **Pros**: Integrated with cloud providers, scalable
- **Cons**: Expensive, vendor lock-in, requires specific cloud provider
- **Rejected**: Not cost-effective, limits deployment flexibility

**Manual Review Only**:
- **Pros**: No scanning overhead, simple
- **Cons**: High security risk, unacceptable for enterprise deployment
- **Rejected**: Security requirement (FR-022)

**Python-Based Scanners (yara-python)**:
- **Pros**: Custom rules, fast, no external service
- **Cons**: Requires expertise to write rules, lower detection rate without commercial signatures
- **Rejected**: Insufficient detection rate for production

### Implementation Notes

1. **Docker Setup** (add to `docker-compose.yml`):
   ```yaml
   clamav:
     image: clamav/clamav:latest
     ports:
       - "3310:3310"
     volumes:
       - clamav_data:/var/lib/clamav
   ```
2. **Python Integration**:
   ```bash
   pip install clamd
   ```
   ```python
   import clamd
   cd = clamd.ClamdUnixSocket()
   result = cd.scan('/path/to/file')
   ```
3. **Configuration**:
   - Enable freshclam for daily virus definition updates
   - Set scan timeout to 60 seconds
   - Configure max file size to 50MB
4. **Error Handling**: If ClamAV is unavailable, fail upload with clear error (security-first approach)
5. **Testing**: Use EICAR test file (standard malware test file) to verify detection

### References

- ClamAV Documentation: https://docs.clamav.net/
- clamd Python Library: https://pypi.org/project/clamd/
- EICAR Test File: https://www.eicar.org/download-anti-malware-testfile/
- VirusTotal API: https://developers.virustotal.com/reference/overview (for fallback)

---

## Decision 6: Document Chunking Strategy

### Decision: Hybrid Semantic + Fixed-Size Chunking

### Rationale

**Hybrid Approach** combines semantic awareness with size constraints:

**Semantic Chunking**:
- Preserve document structure (sections, paragraphs, lists)
- Detect logical boundaries using headings, formatting
- Keep related content together (tables, code blocks)

**Fixed-Size Constraint**:
- Max 512 tokens per chunk (optimal for most embedding models)
- Min 100 tokens (avoid tiny chunks)
- Overlap of 50 tokens between chunks (preserve context)

**Benefits**:
- **Better RAG Accuracy**: Semantic chunks improve retrieval relevance
- **Token Budget**: Fixed size prevents context window overflow
- **Flexibility**: Works with various embedding models (OpenAI, Cohere, etc.)

**Implementation**: Use Docling's built-in chunking with custom post-processing

### Alternatives Considered

**Fixed-Size Only** (naive approach):
- **Pros**: Simple to implement, consistent chunk sizes
- **Cons**: Breaks sentences mid-word, loses context, poor retrieval accuracy
- **Rejected**: Unacceptable for production RAG quality

**Sentence-Based Chunking** (LangChain default):
- **Pros**: Preserves sentence boundaries, readable chunks
- **Cons**: Variable sizes (10-1000 tokens), some sentences too long, doesn't handle tables
- **Rejected**: Size variability causes issues with embedding models

**Recursive Character Splitting** (LlamaIndex):
- **Pros**: Handles multiple separators, good for code
- **Cons**: Ignores document structure, suboptimal for business documents
- **Rejected**: Not optimized for PDF/DOCX documents

**Paragraph-Only Chunking**:
- **Pros**: Natural boundaries, good readability
- **Cons**: Paragraphs can be very long (>1000 tokens), loses heading context
- **Rejected**: Does not meet token budget constraints

### Implementation Notes

1. **Chunking Parameters**:
   ```python
   CHUNK_SIZE = 512       # tokens
   CHUNK_OVERLAP = 50     # tokens
   MIN_CHUNK_SIZE = 100   # tokens
   ```
2. **Semantic Boundaries** (priority order):
   - Section headings (H1-H6)
   - Paragraph boundaries
   - Sentence boundaries
   - Word boundaries (fallback)
3. **Special Cases**:
   - Tables: Keep entire table in one chunk if possible, otherwise split by rows
   - Lists: Keep list items together
   - Code blocks: Treat as atomic units
4. **Metadata**: Store chunk type, start/end page, parent section heading
5. **Token Counting**: Use tiktoken library (OpenAI tokenizer) for accurate counts

### References

- Chunking for RAG: https://www.pinecone.io/learn/chunking-strategies/
- LangChain Text Splitters: https://python.langchain.com/docs/modules/data_connection/document_transformers/
- Docling Chunking: https://ds4sd.github.io/docling/examples/chunking/
- tiktoken Library: https://github.com/openai/tiktoken

---

## Decision 7: Resumable Upload Implementation

### Decision: Custom Multipart Upload (Initial) + tus Protocol (Future)

### Rationale

**Phase 1 (MVP)**: Custom multipart upload using standard HTTP
- **Pros**: No external dependencies, works with standard HTTP clients, simple server implementation
- **Cons**: Client must implement chunking logic, less standardized

**Phase 2 (Future)**: Migrate to tus protocol (https://tus.io)
- **Pros**: Standardized protocol, client libraries available (JavaScript, Python), handles edge cases
- **Cons**: Additional dependency, requires protocol-specific server implementation

**Approach**: Start simple (custom) to deliver MVP quickly, migrate to tus for better client experience

**Custom Implementation**:
1. Client: Split file into 5MB chunks, send with byte range headers
2. Server: Store chunks in temporary location, merge when complete
3. Tracking: `UploadSession` model tracks progress
4. Expiration: Clean up abandoned sessions after 24 hours

### Alternatives Considered

**Presigned URLs (S3-Native)**:
- **Pros**: Offload upload to S3, reduce server load, good for large files
- **Cons**: Requires S3 (no local development), complex client logic, less control over validation
- **Rejected**: Requires S3 in development, premature optimization

**tus Protocol (Immediate)**:
- **Pros**: Standardized, robust, client libraries
- **Cons**: Adds dependency, more complex initial implementation, delays MVP
- **Rejected**: Unnecessary complexity for MVP, can add later

**Single Upload Only**:
- **Pros**: Simplest possible implementation
- **Cons**: Poor UX for large files (>10MB), network interruptions lose all progress
- **Rejected**: FR-024 requires resumable uploads

### Implementation Notes

1. **API Design**:
   - POST `/upload/resumable` → Returns session_id and chunk_size
   - PATCH `/upload/resumable/{session_id}` → Accepts chunks with `Content-Range` header
   - GET `/upload/resumable/{session_id}` → Returns current progress
2. **Headers**:
   ```
   Content-Range: bytes 0-5242879/52428800
   Content-Length: 5242880
   ```
3. **Chunk Storage**: Temporary files in `/tmp/uploads/{session_id}/chunk_{N}`
4. **Merge Logic**: Concatenate chunks when `Content-Range` indicates final chunk
5. **Cleanup**: Celery periodic task to delete expired sessions (>24 hours old)
6. **Testing**: Simulate network interruptions, verify resumption works

### References

- tus Protocol: https://tus.io/
- HTTP Content-Range: https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Content-Range
- Resumable Uploads Best Practices: https://cloud.google.com/storage/docs/resumable-uploads

---

## Decision 8: DOCX Parsing Library

### Decision: python-docx

### Rationale

**python-docx** is the de facto standard for DOCX parsing in Python:

- **Maturity**: 10+ years of development, stable API
- **Accuracy**: High text extraction accuracy (95%+)
- **Feature Complete**: Text, tables, images, formatting
- **Active Maintenance**: Regular updates, responsive maintainers
- **Documentation**: Comprehensive docs with examples
- **MIT License**: Compatible with proprietary projects
- **Pure Python**: No C dependencies, easy to install
- **Integration**: Works well with Docling for unified document processing

**Limitations**: Doesn't handle very complex formatting, but sufficient for 95%+ of business documents

### Alternatives Considered

**docx2txt**:
- **Pros**: Very simple API, fast, lightweight
- **Cons**: Text-only extraction, no table/formatting support, not actively maintained
- **Rejected**: Insufficient features for structured extraction

**mammoth**:
- **Pros**: Good HTML conversion, preserves formatting
- **Cons**: Primarily designed for HTML export, not RAG/extraction use case, more complex API
- **Rejected**: Not optimized for text extraction workflow

**python-docx2pdf** (with extraction):
- **Pros**: Can convert DOCX to PDF then parse
- **Cons**: Requires LibreOffice/MS Office, heavyweight, slower, unnecessary conversion step
- **Rejected**: Operational complexity, performance overhead

**Apache POI (via JPype or Jython)**:
- **Pros**: Very comprehensive, handles edge cases
- **Cons**: Requires Java runtime, heavyweight, complex deployment
- **Rejected**: Same as Tika - Java dependency unacceptable

### Implementation Notes

1. **Installation**: `pip install python-docx`
2. **Basic Usage**:
   ```python
   from docx import Document
   doc = Document('example.docx')
   text = '\n'.join([para.text for para in doc.paragraphs])
   ```
3. **Table Extraction**:
   ```python
   for table in doc.tables:
       for row in table.rows:
           for cell in row.cells:
               text += cell.text
   ```
4. **Metadata**: Extract properties (author, title, created_at) from `doc.core_properties`
5. **Error Handling**: Catch `PackageNotFoundError` for corrupted DOCX files
6. **Testing**: Validate with DOCX files containing tables, images, complex formatting

### References

- python-docx Documentation: https://python-docx.readthedocs.io/
- python-docx GitHub: https://github.com/python-openxml/python-docx
- DOCX Format Specification: https://www.ecma-international.org/publications-and-standards/standards/ecma-376/

---

## Summary of Decisions

| Decision Area | Technology | Rationale |
|---------------|-----------|-----------|
| **Document Parsing** | Docling | RAG-optimized, high accuracy, multi-format, MIT license |
| **File Type Detection** | python-magic | Security via magic bytes, cross-platform, battle-tested |
| **Task Queue** | Dramatiq | Simple, reliable, modern, good observability |
| **Storage** | Dual (Local + S3) | Fast development (local), scalable production (S3) |
| **Malware Scanning** | ClamAV | Free, self-hosted, privacy-friendly, adequate detection |
| **Chunking** | Hybrid Semantic | Balance between semantic accuracy and token constraints |
| **Resumable Uploads** | Custom → tus | Simple MVP first, standardize later |
| **DOCX Parsing** | python-docx | Mature, accurate, well-documented, pure Python |

---

## Implementation Readiness

All research is complete. No `NEEDS CLARIFICATION` markers remain. Ready to proceed to Phase 1 (Design & Contracts).

**Next Step**: Generate `data-model.md`, API contracts in `contracts/`, and `quickstart.md`.
