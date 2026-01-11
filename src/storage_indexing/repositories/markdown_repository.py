"""Markdown repository for markdown-specific database operations.

This module provides repository pattern implementation for markdown metadata and images.
"""

from typing import Any, Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.storage_indexing.models.markdown_metadata import MarkdownMetadata
from src.storage_indexing.models.image_reference import ImageReference


class MarkdownMetadataRepository:
    """Repository for markdown metadata database operations.
    
    Handles markdown metadata CRUD operations.
    
    Example:
        >>> async with async_session() as session:
        ...     repo = MarkdownMetadataRepository(session)
        ...     metadata = await repo.create(metadata_obj)
        ...     await session.commit()
    """
    
    def __init__(self, session: AsyncSession) -> None:
        """Initialize repository with database session.
        
        Args:
            session: SQLAlchemy async session
        """
        self.session = session
    
    async def create(self, metadata: MarkdownMetadata) -> MarkdownMetadata:
        """Create markdown metadata record.
        
        Args:
            metadata: MarkdownMetadata instance to create
        
        Returns:
            Created MarkdownMetadata instance
        """
        self.session.add(metadata)
        await self.session.flush()
        return metadata
    
    async def create_metadata(
        self,
        document_id: int,
        frontmatter: dict[str, Any] | None = None,
        heading_count: int = 0,
        code_block_count: int = 0,
        mermaid_diagram_count: int = 0,
        table_count: int = 0,
        link_count: int = 0,
        image_count: int = 0,
        link_urls: list[str] | None = None,
        has_yaml_frontmatter: bool = False
    ) -> MarkdownMetadata:
        """Create markdown metadata record.
        
        Args:
            document_id: Document identifier
            frontmatter: Parsed YAML frontmatter
            heading_count: Count of headings
            code_block_count: Count of code blocks
            mermaid_diagram_count: Count of Mermaid diagrams
            table_count: Count of tables
            link_count: Count of links
            image_count: Count of images
            link_urls: List of extracted URLs
            has_yaml_frontmatter: Whether frontmatter exists
        
        Returns:
            Created MarkdownMetadata instance
        
        Example:
            >>> metadata = await repo.create_metadata(
            ...     document_id=1001,
            ...     frontmatter={"title": "API Docs", "author": "John"},
            ...     heading_count=12,
            ...     code_block_count=8,
            ...     has_yaml_frontmatter=True
            ... )
        """
        metadata = MarkdownMetadata(
            document_id=document_id,
            frontmatter=frontmatter,
            heading_count=heading_count,
            code_block_count=code_block_count,
            mermaid_diagram_count=mermaid_diagram_count,
            table_count=table_count,
            link_count=link_count,
            image_count=image_count,
            link_urls=link_urls,
            has_yaml_frontmatter=has_yaml_frontmatter
        )
        self.session.add(metadata)
        await self.session.flush()
        return metadata
    
    async def get_metadata_by_document(
        self,
        document_id: int
    ) -> MarkdownMetadata | None:
        """Get markdown metadata for a document.
        
        Args:
            document_id: Document identifier
        
        Returns:
            MarkdownMetadata if found, None otherwise
        
        Example:
            >>> metadata = await repo.get_metadata_by_document(document_id=1001)
            >>> if metadata and metadata.has_yaml_frontmatter:
            ...     print(metadata.frontmatter)
        """
        result = await self.session.execute(
            select(MarkdownMetadata)
            .where(MarkdownMetadata.document_id == document_id)
        )
        return result.scalar_one_or_none()


class ImageReferenceRepository:
    """Repository for image reference database operations.
    
    Handles image reference CRUD operations.
    """
    
    def __init__(self, session: AsyncSession) -> None:
        """Initialize repository with database session.
        
        Args:
            session: SQLAlchemy async session
        """
        self.session = session
    
    async def create(self, image_ref: ImageReference) -> ImageReference:
        """Create image reference record.
        
        Args:
            image_ref: ImageReference instance to create
        
        Returns:
            Created ImageReference instance
        """
        self.session.add(image_ref)
        await self.session.flush()
        return image_ref
    
    async def create_image_reference(
        self,
        document_id: int,
        image_url: str,
        alt_text: str | None = None,
        is_local_path: bool = False,
        is_base64: bool = False,
        is_external_url: bool = True,
        resolved_path: str | None = None,
        file_size_bytes: int | None = None,
        ocr_pending: bool = False,
        position_in_document: int | None = None
    ) -> ImageReference:
        """Create image reference record.
        
        Args:
            document_id: Document identifier
            image_url: Image URL/path from markdown
            alt_text: Alt text from markdown
            is_local_path: True if local file path
            is_base64: True if base64 embedded
            is_external_url: True if http/https URL
            resolved_path: Absolute path if local
            file_size_bytes: Image file size
            ocr_pending: Flag for future OCR
            position_in_document: Line number
        
        Returns:
            Created ImageReference instance
        
        Example:
            >>> ref = await repo.create_image_reference(
            ...     document_id=1001,
            ...     image_url="./images/diagram.png",
            ...     alt_text="Architecture diagram",
            ...     is_local_path=True,
            ...     resolved_path="/uploads/doc_1001/images/diagram.png"
            ... )
        """
        ref = ImageReference(
            document_id=document_id,
            image_url=image_url,
            alt_text=alt_text,
            is_local_path=is_local_path,
            is_base64=is_base64,
            is_external_url=is_external_url,
            resolved_path=resolved_path,
            file_size_bytes=file_size_bytes,
            ocr_pending=ocr_pending,
            position_in_document=position_in_document
        )
        self.session.add(ref)
        await self.session.flush()
        return ref
    
    async def create_image_references_batch(
        self,
        image_refs: list[dict[str, Any]]
    ) -> list[ImageReference]:
        """Create multiple image references in a batch.
        
        Args:
            image_refs: List of image reference dicts
        
        Returns:
            List of created ImageReference instances
        
        Example:
            >>> refs = await repo.create_image_references_batch([
            ...     {
            ...         "document_id": 1001,
            ...         "image_url": "https://example.com/img1.png",
            ...         "alt_text": "Diagram 1"
            ...     },
            ...     {
            ...         "document_id": 1001,
            ...         "image_url": "./img2.png",
            ...         "is_local_path": True
            ...     }
            ... ])
        """
        refs = [ImageReference(**ref_data) for ref_data in image_refs]
        self.session.add_all(refs)
        await self.session.flush()
        return refs
    
    async def get_images_by_document(
        self,
        document_id: int
    ) -> Sequence[ImageReference]:
        """Get all image references for a document.
        
        Args:
            document_id: Document identifier
        
        Returns:
            List of ImageReference instances
        
        Example:
            >>> images = await repo.get_images_by_document(document_id=1001)
            >>> for img in images:
            ...     print(f"{img.image_type}: {img.image_url}")
        """
        result = await self.session.execute(
            select(ImageReference)
            .where(ImageReference.document_id == document_id)
            .order_by(ImageReference.position_in_document)
        )
        return result.scalars().all()
    
    async def get_images_by_type(
        self,
        document_id: int,
        image_type: str
    ) -> Sequence[ImageReference]:
        """Get image references by type (local, base64, external).
        
        Args:
            document_id: Document identifier
            image_type: Image type filter ('local', 'base64', 'external')
        
        Returns:
            Filtered list of ImageReference instances
        
        Example:
            >>> local_images = await repo.get_images_by_type(
            ...     document_id=1001,
            ...     image_type="local"
            ... )
        """
        query = select(ImageReference).where(ImageReference.document_id == document_id)
        
        if image_type == "local":
            query = query.where(ImageReference.is_local_path == True)
        elif image_type == "base64":
            query = query.where(ImageReference.is_base64 == True)
        elif image_type == "external":
            query = query.where(ImageReference.is_external_url == True)
        
        result = await self.session.execute(query)
        return result.scalars().all()
    
    async def get_pending_ocr_images(
        self,
        tenant_id: int,
        limit: int = 100
    ) -> Sequence[ImageReference]:
        """Get images pending OCR processing.
        
        Args:
            tenant_id: Tenant identifier for filtering
            limit: Maximum results to return
        
        Returns:
            List of ImageReference instances with ocr_pending=True
        
        Example:
            >>> pending_images = await repo.get_pending_ocr_images(
            ...     tenant_id=1,
            ...     limit=50
            ... )
        """
        result = await self.session.execute(
            select(ImageReference)
            .join(ImageReference.document)
            .where(ImageReference.ocr_pending == True)
            .where(ImageReference.document.has(tenant_id=tenant_id))
            .limit(limit)
        )
        return result.scalars().all()
