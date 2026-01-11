"""Document parsing orchestration service."""

import structlog

from src.ingestion_parsing.parsers.parser_factory import ParserFactory
from src.ingestion_parsing.services.chunking_service import ChunkingService
from src.storage_indexing.models import JobStatus, ProcessingStatus
from src.storage_indexing.repositories.chunk_repository import ChunkRepository
from src.storage_indexing.repositories.document_repository import DocumentRepository
from src.storage_indexing.repositories.job_repository import JobRepository
from src.storage_indexing.repositories.markdown_repository import (
    ImageReferenceRepository,
    MarkdownMetadataRepository,
)

logger = structlog.get_logger(__name__)


class ParsingService:
    """Service for orchestrating document parsing workflow.
    
    Coordinates:
    1. Get appropriate parser for document type
    2. Extract text and metadata
    3. Chunk document for RAG
    4. Store chunks in database
    5. Update document and job status
    
    Example:
        >>> service = ParsingService(document_repo, chunk_repo, job_repo)
        >>> await service.parse_document(document_id=123)
    """

    def __init__(
        self,
        document_repo: DocumentRepository,
        chunk_repo: ChunkRepository,
        job_repo: JobRepository,
        markdown_metadata_repo: MarkdownMetadataRepository | None = None,
        image_reference_repo: ImageReferenceRepository | None = None,
    ) -> None:
        """Initialize parsing service.
        
        Args:
            document_repo: Document repository
            chunk_repo: Chunk repository
            job_repo: Job repository
            markdown_metadata_repo: Markdown metadata repository (optional)
            image_reference_repo: Image reference repository (optional)
        """
        self.document_repo = document_repo
        self.chunk_repo = chunk_repo
        self.job_repo = job_repo
        self.markdown_metadata_repo = markdown_metadata_repo
        self.image_reference_repo = image_reference_repo
        self.chunking_service = ChunkingService()

    async def parse_document(self, document_id: int) -> None:
        """Parse document and create chunks.
        
        Complete workflow:
        1. Get document from database (0% progress)
        2. Get appropriate parser (25% progress)
        3. Extract text and metadata (50% progress)
        4. Chunk document (75% progress)
        5. Store chunks in database (90% progress)
        6. Update document status (100% progress)
        
        Args:
            document_id: ID of document to parse
            
        Raises:
            FileNotFoundError: If document file not found
            ValueError: If parsing fails
        """
        logger.info("Starting document parsing", document_id=document_id)
        
        try:
            # Get document
            document = await self.document_repo.get_by_id(document_id, tenant_id=0)
            if not document:
                raise ValueError(f"Document {document_id} not found")
            
            # Get associated job (if exists)
            jobs = await self.job_repo.get_by_document(document_id)
            job = jobs[0] if jobs else None
            
            if job:
                await self.job_repo.update_status(
                    job_id=job.job_id,
                    status=JobStatus.PROCESSING.value,
                    progress_percent=0,
                )
            
            # Step 1: Get parser (25%)
            parser = ParserFactory.get_parser(document.mime_type)
            
            if job:
                await self.job_repo.update_status(
                    job_id=job.job_id,
                    status=JobStatus.PROCESSING.value,
                    progress_percent=25,
                )
            
            # Step 2: Extract text and metadata (50%)
            logger.info("Extracting text", document_id=document_id, storage_path=document.storage_path)
            parsing_result = parser.parse(document.storage_path)
            
            if job:
                await self.job_repo.update_status(
                    job_id=job.job_id,
                    status=JobStatus.PROCESSING.value,
                    progress_percent=50,
                )
            
            # Step 3: Chunk document (75%)
            logger.info("Chunking document", document_id=document_id, text_length=len(parsing_result.text_content))
            chunks = self.chunking_service.chunk_document(
                text=parsing_result.text_content,
                document_id=document_id,
            )
            
            if job:
                await self.job_repo.update_status(
                    job_id=job.job_id,
                    status=JobStatus.PROCESSING.value,
                    progress_percent=75,
                )
            
            # Step 4: Store chunks (90%)
            logger.info("Storing chunks", document_id=document_id, chunk_count=len(chunks))
            for chunk in chunks:
                await self.chunk_repo.create(
                    document_id=document_id,
                    chunk_index=chunk.chunk_index,
                    content=chunk.content,
                    chunk_type=chunk.chunk_type,
                    start_page=chunk.start_page,
                    end_page=chunk.end_page,
                    token_count=chunk.token_count,
                    parent_heading=chunk.parent_heading,
                )
            
            if job:
                await self.job_repo.update_status(
                    job_id=job.job_id,
                    status=JobStatus.PROCESSING.value,
                    progress_percent=90,
                )
            
            # Step 5: Store markdown-specific metadata (if markdown document)
            if document.mime_type in ["text/markdown", "text/x-markdown"]:
                await self._store_markdown_metadata(document_id, parsing_result.metadata)
                logger.info(
                    "Markdown metadata stored",
                    document_id=document_id,
                    heading_count=parsing_result.metadata.get("heading_count", 0),
                    image_count=parsing_result.metadata.get("image_count", 0),
                )
            
            # Step 6: Update document status (100%)
            await self.document_repo.update_status(
                document_id=document_id,
                status=ProcessingStatus.PARSED.value,
                language=parsing_result.language,
                page_count=parsing_result.page_count,
            )
            
            if job:
                await self.job_repo.update_status(
                    job_id=job.job_id,
                    status=JobStatus.COMPLETED.value,
                    progress_percent=100,
                )
            
            logger.info(
                "Document parsing completed",
                document_id=document_id,
                chunk_count=len(chunks),
                page_count=parsing_result.page_count,
            )
            
        except Exception as e:
            logger.error(
                "Document parsing failed",
                document_id=document_id,
                error=str(e),
                error_type=type(e).__name__,
            )
            
            # Update job status to failed
            if job:
                await self.job_repo.update_status(
                    job_id=job.job_id,
                    status=JobStatus.FAILED.value,
                    error_message=str(e),
                )
            
            # Update document status to failed
            await self.document_repo.update_status(
                document_id=document_id,
                status=ProcessingStatus.FAILED.value,
            )
            
            raise

    async def _store_markdown_metadata(
        self, document_id: int, metadata: dict
    ) -> None:
        """Store markdown-specific metadata and image references.
        
        Args:
            document_id: ID of the document
            metadata: Parsed metadata dictionary containing markdown-specific fields
        """
        if not self.markdown_metadata_repo:
            logger.warning(
                "Markdown metadata repository not provided, skipping metadata storage",
                document_id=document_id,
            )
            return
        
        # Create MarkdownMetadata record
        from src.storage_indexing.models.markdown_metadata import MarkdownMetadata
        
        markdown_metadata = MarkdownMetadata(
            document_id=document_id,
            frontmatter=metadata.get("frontmatter"),
            heading_count=metadata.get("heading_count", 0),
            code_block_count=metadata.get("code_block_count", 0),
            mermaid_diagram_count=metadata.get("mermaid_diagram_count", 0),
            table_count=metadata.get("table_count", 0),
            link_count=metadata.get("link_count", 0),
            image_count=metadata.get("image_count", 0),
            link_urls=metadata.get("link_urls", []),
            has_yaml_frontmatter=metadata.get("has_yaml_frontmatter", False),
        )
        
        await self.markdown_metadata_repo.create(markdown_metadata)
        
        # Create ImageReference records
        if self.image_reference_repo and metadata.get("image_references"):
            from src.storage_indexing.models.image_reference import ImageReference
            
            for idx, img_ref in enumerate(metadata["image_references"]):
                image_reference = ImageReference(
                    document_id=document_id,
                    image_url=img_ref["image_url"],
                    alt_text=img_ref.get("alt_text"),
                    is_local_path=img_ref.get("is_local_path", False),
                    is_base64=img_ref.get("is_base64", False),
                    is_external_url=img_ref.get("is_external_url", True),
                    resolved_path=img_ref.get("resolved_path"),
                    position_in_document=img_ref.get("position", idx),
                )
                await self.image_reference_repo.create(image_reference)
