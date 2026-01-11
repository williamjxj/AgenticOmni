"""Application settings using Pydantic BaseSettings.

This module defines the Settings class that loads and validates environment variables.
All configuration should be accessed through the settings instance in src.shared.config.
"""

from pydantic import Field, PostgresDsn, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


def parse_cors(v: str | list[str] | None) -> list[str]:
    """Parse CORS origins from comma-separated string or list."""
    if v is None or v == "":
        return ["http://localhost:3000"]
    if isinstance(v, str):
        return [origin.strip() for origin in v.split(",") if origin.strip()]
    return v


class Settings(BaseSettings):
    """Application configuration loaded from environment variables.

    All settings are loaded from environment variables or .env file.
    Required settings will raise validation errors if missing.
    Optional settings have sensible defaults.

    Example:
        >>> from config.settings import Settings
        >>> settings = Settings()
        >>> print(settings.database_url)
        postgresql+asyncpg://user:pass@localhost/db
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",  # Ignore extra environment variables
    )

    # ========================================================================
    # Database Configuration
    # ========================================================================
    database_url: PostgresDsn = Field(
        ...,
        description="PostgreSQL connection URL with asyncpg driver",
        examples=["postgresql+asyncpg://user:pass@localhost:5436/agenticomni"],
    )

    database_pool_size: int = Field(
        default=5,
        ge=1,
        le=20,
        description="Database connection pool size",
    )

    database_max_overflow: int = Field(
        default=10,
        ge=0,
        le=50,
        description="Maximum overflow connections beyond pool_size",
    )

    # ========================================================================
    # Vector Store Configuration
    # ========================================================================
    vector_dimensions: int = Field(
        default=1536,
        ge=384,
        le=4096,
        description="Embedding vector dimensions (must match embedding model)",
    )

    # ========================================================================
    # API Server Configuration
    # ========================================================================
    api_host: str = Field(
        default="0.0.0.0",
        description="API server host address",
    )

    api_port: int = Field(
        default=8000,
        ge=1024,
        le=65535,
        description="API server port",
    )

    cors_origins: str = Field(
        default="http://localhost:3000",
        description="Allowed CORS origins (comma-separated)",
    )

    def get_cors_origins_list(self) -> list[str]:
        """Get CORS origins as a list."""
        return parse_cors(self.cors_origins)

    # ========================================================================
    # Logging Configuration
    # ========================================================================
    log_level: str = Field(
        default="INFO",
        description="Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)",
    )

    @field_validator("log_level")
    @classmethod
    def validate_log_level(cls, v: str) -> str:
        """Validate log level is one of the standard levels."""
        allowed_levels = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
        v_upper = v.upper()
        if v_upper not in allowed_levels:
            raise ValueError(f"log_level must be one of {allowed_levels}, got {v}")
        return v_upper

    log_format: str = Field(
        default="json",
        description="Log format: json or console",
    )

    # ========================================================================
    # Security Configuration
    # ========================================================================
    secret_key: str = Field(
        ...,
        min_length=32,
        description="Secret key for JWT tokens, session encryption, etc.",
    )

    enforce_tenant_isolation: bool = Field(
        default=True,
        description="Enforce row-level tenant isolation in database queries",
    )

    # ========================================================================
    # Optional: LLM API Keys
    # ========================================================================
    openai_api_key: str | None = Field(
        default=None,
        description="OpenAI API key for embeddings and chat completion",
    )

    anthropic_api_key: str | None = Field(
        default=None,
        description="Anthropic API key for Claude models",
    )

    # ========================================================================
    # Malware Scanning Configuration
    # ========================================================================
    enable_malware_scanning: bool = Field(
        default=False,
        description="Enable malware scanning with ClamAV",
    )

    clamav_host: str = Field(
        default="localhost",
        description="ClamAV daemon host",
    )

    clamav_port: int = Field(
        default=3310,
        ge=1,
        le=65535,
        description="ClamAV daemon port",
    )

    clamav_timeout: int = Field(
        default=30,
        ge=1,
        le=300,
        description="ClamAV scan timeout in seconds",
    )

    # ========================================================================
    # Redis Configuration
    # ========================================================================
    redis_url: str = Field(
        default="redis://localhost:6379/0",
        description="Redis connection URL",
    )

    redis_max_connections: int = Field(
        default=10,
        ge=1,
        le=100,
        description="Maximum Redis connections in pool",
    )

    # ========================================================================
    # Application Configuration
    # ========================================================================
    environment: str = Field(
        default="development",
        description="Application environment: development, staging, production",
    )

    debug: bool = Field(
        default=False,
        description="Enable debug mode (detailed errors, auto-reload)",
    )

    api_version: str = Field(
        default="v1",
        description="API version prefix",
    )

    # ========================================================================
    # Document Upload Configuration (T013)
    # ========================================================================
    storage_backend: str = Field(
        default="local",
        description="Storage backend: local or s3",
    )

    upload_dir: str = Field(
        default="./uploads",
        description="Directory for uploaded files (local storage)",
    )

    temp_upload_dir: str = Field(
        default="./tmp/uploads",
        description="Directory for temporary upload chunks",
    )

    max_upload_size_mb: int = Field(
        default=50,
        ge=1,
        le=1000,
        description="Maximum file upload size in MB",
    )

    max_batch_size: int = Field(
        default=10,
        ge=1,
        le=50,
        description="Maximum number of files per batch upload",
    )

    allowed_file_types: str = Field(
        default="pdf,docx,txt,md,markdown",
        description="Allowed file types for upload (comma-separated)",
    )

    def get_allowed_file_types_list(self) -> list[str]:
        """Get allowed file types as a list."""
        return [ft.strip().lower() for ft in self.allowed_file_types.split(",") if ft.strip()]

    # Chunking configuration for RAG
    chunk_size_tokens: int = Field(
        default=512,
        ge=100,
        le=2000,
        description="Target chunk size in tokens",
    )

    chunk_overlap_tokens: int = Field(
        default=50,
        ge=0,
        le=500,
        description="Overlap between chunks in tokens",
    )

    min_chunk_size_tokens: int = Field(
        default=100,
        ge=10,
        le=1000,
        description="Minimum chunk size in tokens",
    )

    # S3 configuration (optional)
    s3_bucket: str | None = Field(
        default=None,
        description="S3 bucket name for document storage",
    )

    s3_region: str | None = Field(
        default=None,
        description="AWS region for S3 bucket",
    )

    aws_access_key_id: str | None = Field(
        default=None,
        description="AWS access key ID",
    )

    aws_secret_access_key: str | None = Field(
        default=None,
        description="AWS secret access key",
    )

    # ========================================================================
    # Task Queue Configuration (T014)
    # ========================================================================
    dramatiq_broker_url: str = Field(
        default="redis://localhost:6379/1",
        description="Dramatiq broker URL (Redis)",
    )

    dramatiq_result_backend: str = Field(
        default="redis://localhost:6379/1",
        description="Dramatiq result backend URL",
    )

    max_concurrent_parsing_jobs: int = Field(
        default=5,
        ge=1,
        le=50,
        description="Maximum concurrent parsing jobs",
    )

    parsing_timeout_seconds: int = Field(
        default=300,
        ge=30,
        le=3600,
        description="Parsing timeout in seconds",
    )

    # ========================================================================
    # Markdown Ingestion Configuration (T008)
    # ========================================================================
    markdown_max_file_size_mb: int = Field(
        default=10,
        ge=1,
        le=100,
        description="Maximum markdown file size in MB",
    )

    folder_max_files: int = Field(
        default=500,
        ge=1,
        le=5000,
        description="Maximum number of files per folder upload",
    )

    folder_max_depth: int = Field(
        default=20,
        ge=1,
        le=50,
        description="Maximum folder depth for recursive traversal",
    )

    markdown_html_stripping_mode: str = Field(
        default="strip",
        description="HTML handling mode: strip or preserve",
    )

    @field_validator("markdown_html_stripping_mode")
    @classmethod
    def validate_html_mode(cls, v: str) -> str:
        """Validate HTML stripping mode."""
        allowed_modes = {"strip", "preserve"}
        v_lower = v.lower()
        if v_lower not in allowed_modes:
            raise ValueError(f"markdown_html_stripping_mode must be one of {allowed_modes}, got {v}")
        return v_lower

    # ========================================================================
    # LLM Configuration (DeepSeek, OpenAI, etc.)
    # ========================================================================
    llm_provider: str = Field(
        default="deepseek",
        description="LLM provider: deepseek, openai, anthropic",
    )

    # DeepSeek Configuration
    deepseek_api_key: str | None = Field(
        default=None,
        description="DeepSeek API key for chat completions",
    )

    deepseek_api_base: str = Field(
        default="https://api.deepseek.com/v1",
        description="DeepSeek API base URL",
    )

    deepseek_model: str = Field(
        default="deepseek-chat",
        description="DeepSeek model name (deepseek-chat, deepseek-coder)",
    )

    deepseek_temperature: float = Field(
        default=0.7,
        ge=0.0,
        le=2.0,
        description="DeepSeek temperature for response randomness",
    )

    deepseek_max_tokens: int = Field(
        default=4096,
        ge=1,
        le=32768,
        description="DeepSeek max tokens per response",
    )

    # Embedding Configuration
    embedding_provider: str = Field(
        default="openai",
        description="Embedding provider: openai, huggingface, deepseek, ollama",
    )

    @field_validator("embedding_provider")
    @classmethod
    def validate_embedding_provider(cls, v: str) -> str:
        """Validate embedding provider selection."""
        allowed_providers = {"openai", "huggingface", "deepseek", "ollama"}
        v_lower = v.lower()
        if v_lower not in allowed_providers:
            raise ValueError(f"embedding_provider must be one of {allowed_providers}, got {v}")
        return v_lower

    embedding_model: str = Field(
        default="text-embedding-3-small",
        description="Embedding model name",
    )

    embedding_dimension: int = Field(
        default=1536,
        ge=128,
        le=4096,
        description="Embedding vector dimension (must match vector_dimensions)",
    )

    ollama_base_url: str = Field(
        default="http://localhost:11434",
        description="Ollama API base URL",
    )

    # ========================================================================
    # OCR Configuration (Feature 004-ocr-embedding-pipeline)
    # ========================================================================
    ocr_engine: str = Field(
        default="auto",
        description="OCR engine: auto, paddleocr, tesseract",
    )

    @field_validator("ocr_engine")
    @classmethod
    def validate_ocr_engine(cls, v: str) -> str:
        """Validate OCR engine selection."""
        allowed_engines = {"auto", "paddleocr", "tesseract"}
        v_lower = v.lower()
        if v_lower not in allowed_engines:
            raise ValueError(f"ocr_engine must be one of {allowed_engines}, got {v}")
        return v_lower

    ocr_languages: str = Field(
        default="en,zh",
        description="Supported OCR languages (comma-separated ISO 639-1 codes)",
    )

    def get_ocr_languages_list(self) -> list[str]:
        """Get OCR languages as a list."""
        return [lang.strip().lower() for lang in self.ocr_languages.split(",") if lang.strip()]

    ocr_confidence_threshold: float = Field(
        default=0.7,
        ge=0.0,
        le=1.0,
        description="Minimum confidence threshold for OCR text acceptance",
    )

    ocr_gpu_enabled: bool = Field(
        default=True,
        description="Enable GPU acceleration for OCR processing",
    )

    ocr_max_concurrent_jobs: int = Field(
        default=4,
        ge=1,
        le=20,
        description="Maximum concurrent OCR jobs",
    )

    # ========================================================================
    # Local Embedding Configuration (Feature 004-ocr-embedding-pipeline)
    # ========================================================================
    local_embedding_model: str = Field(
        default="intfloat/multilingual-e5-base",
        description="Local embedding model from HuggingFace (sentence-transformers)",
    )

    embedding_batch_size: int = Field(
        default=32,
        ge=1,
        le=128,
        description="Batch size for embedding generation",
    )

    embedding_gpu_enabled: bool = Field(
        default=True,
        description="Enable GPU acceleration for embedding generation",
    )

    embedding_model_cache: str | None = Field(
        default=None,
        description="Custom cache directory for embedding models",
    )

    # ========================================================================
    # Document Chunking Configuration (Feature 004-ocr-embedding-pipeline)
    # ========================================================================
    max_chunk_size: int = Field(
        default=500,
        ge=100,
        le=1000,
        description="Maximum chunk size in tokens",
    )

    chunk_overlap: int = Field(
        default=50,
        ge=0,
        le=200,
        description="Chunk overlap in tokens",
    )

    max_document_size_mb: int = Field(
        default=100,
        ge=1,
        le=500,
        description="Maximum document size in MB",
    )

    max_document_pages: int = Field(
        default=500,
        ge=1,
        le=2000,
        description="Maximum pages per document",
    )

    # ========================================================================
    # Vector Search Configuration (Feature 004-ocr-embedding-pipeline)
    # ========================================================================
    search_default_limit: int = Field(
        default=10,
        ge=1,
        le=100,
        description="Default number of search results",
    )

    search_max_limit: int = Field(
        default=100,
        ge=1,
        le=500,
        description="Maximum number of search results",
    )

    search_min_similarity: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Minimum similarity score for search results",
    )

    hnsw_m: int = Field(
        default=16,
        ge=4,
        le=64,
        description="HNSW index M parameter (connections per layer)",
    )

    hnsw_ef_construction: int = Field(
        default=64,
        ge=16,
        le=256,
        description="HNSW index ef_construction parameter (build quality)",
    )

    # ========================================================================
    # Background Job Configuration (Feature 004-ocr-embedding-pipeline)
    # ========================================================================
    max_job_retries: int = Field(
        default=3,
        ge=0,
        le=10,
        description="Maximum retry attempts for failed jobs",
    )

    default_job_priority: int = Field(
        default=5,
        ge=1,
        le=10,
        description="Default job priority (1=highest, 10=lowest)",
    )

    max_concurrent_jobs: int = Field(
        default=4,
        ge=1,
        le=20,
        description="Maximum concurrent processing jobs",
    )

    # RAG Configuration
    rag_enabled: bool = Field(
        default=True,
        description="Enable RAG query functionality",
    )

    rag_temperature: float = Field(
        default=0.3,
        ge=0.0,
        le=1.0,
        description="RAG query temperature (lower = more factual)",
    )

    rag_top_k: int = Field(
        default=5,
        ge=1,
        le=20,
        description="Number of chunks to retrieve for RAG context",
    )

    rag_context_window: int = Field(
        default=8000,
        ge=1000,
        le=32000,
        description="Maximum context window size for RAG queries",
    )

    rag_similarity_threshold: float = Field(
        default=0.7,
        ge=0.0,
        le=1.0,
        description="Minimum similarity score for chunk retrieval",
    )

    # ========================================================================
    # Property Methods
    # ========================================================================
    @property
    def is_development(self) -> bool:
        """Check if running in development environment."""
        return self.environment.lower() == "development"

    @property
    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.environment.lower() == "production"

    @property
    def max_upload_size_bytes(self) -> int:
        """Get maximum upload size in bytes."""
        return self.max_upload_size_mb * 1024 * 1024
