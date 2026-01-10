"""Document parsing orchestration service."""

import structlog

from src.ingestion_parsing.parsers.parser_factory import ParserFactory
from src.ingestion_parsing.services.chunking_service import ChunkingService
from src.storage_indexing.models import ProcessingStatus
from src.storage_indexing.repositories.chunk_repository import ChunkRepository
from src.storage_indexing.repositories.document_repository import DocumentRepository
from src.storage_indexing.repositories.job_repository import JobRepository

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
    ) -> None:
        """Initialize parsing service.
        
        Args:
            document_repo: Document repository
            chunk_repo: Chunk repository
            job_repo: Job repository
        """
        self.document_repo = document_repo
        self.chunk_repo = chunk_repo
        self.job_repo = job_repo
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
                    status=ProcessingStatus.PROCESSING.value,
                    progress_percent=0,
                )
            
            # Step 1: Get parser (25%)
            parser = ParserFactory.get_parser(document.mime_type)
            
            if job:
                await self.job_repo.update_status(
                    job_id=job.job_id,
                    status=ProcessingStatus.PROCESSING.value,
                    progress_percent=25,
                )
            
            # Step 2: Extract text and metadata (50%)
            logger.info("Extracting text", document_id=document_id, storage_path=document.storage_path)
            parsing_result = parser.parse(document.storage_path)
            
            if job:
                await self.job_repo.update_status(
                    job_id=job.job_id,
                    status=ProcessingStatus.PROCESSING.value,
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
                    status=ProcessingStatus.PROCESSING.value,
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
                    status=ProcessingStatus.PROCESSING.value,
                    progress_percent=90,
                )
            
            # Step 5: Update document status (100%)
            await self.document_repo.update_status(
                document_id=document_id,
                status=ProcessingStatus.PARSED.value,
                language=parsing_result.language,
                page_count=parsing_result.page_count,
            )
            
            if job:
                await self.job_repo.update_status(
                    job_id=job.job_id,
                    status=ProcessingStatus.COMPLETED.value,
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
                    status=ProcessingStatus.FAILED.value,
                    error_message=str(e),
                )
            
            # Update document status to failed
            await self.document_repo.update_status(
                document_id=document_id,
                status=ProcessingStatus.FAILED.value,
            )
            
            raise
