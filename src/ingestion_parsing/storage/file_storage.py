"""File storage abstraction layer for document uploads.

This module provides an abstract interface for file storage with implementations
for local filesystem and S3-compatible object storage.
"""

import shutil
from abc import ABC, abstractmethod
from pathlib import Path
from typing import BinaryIO

import aiofiles
import boto3
from botocore.exceptions import ClientError

import structlog

logger = structlog.get_logger(__name__)


class FileStorage(ABC):
    """Abstract base class for file storage backends.
    
    This interface allows switching between local filesystem storage (development)
    and S3-compatible object storage (production) without changing application code.
    """

    @abstractmethod
    async def upload(self, file_path: str, storage_key: str) -> str:
        """Upload a file to storage.
        
        Args:
            file_path: Local path to the file to upload
            storage_key: Storage key/path where file should be stored
            
        Returns:
            Storage path or URL where file was stored
            
        Raises:
            FileNotFoundError: If source file does not exist
            IOError: If upload fails
        """
        pass

    @abstractmethod
    async def download(self, storage_key: str) -> bytes:
        """Download a file from storage.
        
        Args:
            storage_key: Storage key/path of the file
            
        Returns:
            File content as bytes
            
        Raises:
            FileNotFoundError: If file does not exist in storage
            IOError: If download fails
        """
        pass

    @abstractmethod
    async def delete(self, storage_key: str) -> None:
        """Delete a file from storage.
        
        Args:
            storage_key: Storage key/path of the file
            
        Raises:
            FileNotFoundError: If file does not exist in storage
            IOError: If deletion fails
        """
        pass

    @abstractmethod
    async def exists(self, storage_key: str) -> bool:
        """Check if a file exists in storage.
        
        Args:
            storage_key: Storage key/path of the file
            
        Returns:
            True if file exists, False otherwise
        """
        pass


class LocalFileStorage(FileStorage):
    """Local filesystem storage implementation for development.
    
    Stores files in a local directory with tenant isolation via subdirectories.
    
    Example:
        >>> storage = LocalFileStorage(base_dir="./uploads")
        >>> await storage.upload("/tmp/doc.pdf", "tenant1/doc123.pdf")
        ./uploads/tenant1/doc123.pdf
    """

    def __init__(self, base_dir: str) -> None:
        """Initialize local file storage.
        
        Args:
            base_dir: Base directory for file storage
        """
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)
        logger.info("Initialized local file storage", base_dir=str(self.base_dir))

    async def upload(self, file_path: str, storage_key: str) -> str:
        """Upload file to local filesystem."""
        source = Path(file_path)
        if not source.exists():
            raise FileNotFoundError(f"Source file not found: {file_path}")

        destination = self.base_dir / storage_key
        destination.parent.mkdir(parents=True, exist_ok=True)

        # Copy file asynchronously
        async with aiofiles.open(source, "rb") as src:
            async with aiofiles.open(destination, "wb") as dst:
                content = await src.read()
                await dst.write(content)

        logger.info("File uploaded to local storage", storage_key=storage_key, size=source.stat().st_size)
        return str(destination)

    async def download(self, storage_key: str) -> bytes:
        """Download file from local filesystem."""
        file_path = self.base_dir / storage_key
        
        if not file_path.exists():
            raise FileNotFoundError(f"File not found in storage: {storage_key}")

        async with aiofiles.open(file_path, "rb") as f:
            content = await f.read()

        logger.info("File downloaded from local storage", storage_key=storage_key, size=len(content))
        return content

    async def delete(self, storage_key: str) -> None:
        """Delete file from local filesystem."""
        file_path = self.base_dir / storage_key
        
        if not file_path.exists():
            raise FileNotFoundError(f"File not found in storage: {storage_key}")

        file_path.unlink()
        logger.info("File deleted from local storage", storage_key=storage_key)

    async def exists(self, storage_key: str) -> bool:
        """Check if file exists in local filesystem."""
        file_path = self.base_dir / storage_key
        return file_path.exists()


class S3FileStorage(FileStorage):
    """S3-compatible object storage implementation for production.
    
    Stores files in an S3 bucket with tenant isolation via key prefixes.
    
    Example:
        >>> storage = S3FileStorage(
        ...     bucket="my-documents",
        ...     region="us-east-1",
        ...     access_key="...",
        ...     secret_key="..."
        ... )
        >>> await storage.upload("/tmp/doc.pdf", "tenant1/doc123.pdf")
        s3://my-documents/tenant1/doc123.pdf
    """

    def __init__(
        self,
        bucket: str,
        region: str | None = None,
        access_key: str | None = None,
        secret_key: str | None = None,
    ) -> None:
        """Initialize S3 file storage.
        
        Args:
            bucket: S3 bucket name
            region: AWS region (optional, uses default if not provided)
            access_key: AWS access key ID (optional, uses IAM role if not provided)
            secret_key: AWS secret access key (optional, uses IAM role if not provided)
        """
        self.bucket = bucket
        self.region = region

        # Initialize S3 client
        session_kwargs = {}
        if access_key and secret_key:
            session_kwargs["aws_access_key_id"] = access_key
            session_kwargs["aws_secret_access_key"] = secret_key
        if region:
            session_kwargs["region_name"] = region

        self.s3_client = boto3.client("s3", **session_kwargs)
        logger.info("Initialized S3 file storage", bucket=bucket, region=region)

    async def upload(self, file_path: str, storage_key: str) -> str:
        """Upload file to S3."""
        source = Path(file_path)
        if not source.exists():
            raise FileNotFoundError(f"Source file not found: {file_path}")

        try:
            self.s3_client.upload_file(str(source), self.bucket, storage_key)
            logger.info("File uploaded to S3", bucket=self.bucket, key=storage_key, size=source.stat().st_size)
            return f"s3://{self.bucket}/{storage_key}"
        except ClientError as e:
            logger.error("S3 upload failed", error=str(e), bucket=self.bucket, key=storage_key)
            raise IOError(f"Failed to upload file to S3: {e}") from e

    async def download(self, storage_key: str) -> bytes:
        """Download file from S3."""
        try:
            response = self.s3_client.get_object(Bucket=self.bucket, Key=storage_key)
            content = response["Body"].read()
            logger.info("File downloaded from S3", bucket=self.bucket, key=storage_key, size=len(content))
            return content
        except ClientError as e:
            if e.response["Error"]["Code"] == "NoSuchKey":
                raise FileNotFoundError(f"File not found in S3: {storage_key}") from e
            logger.error("S3 download failed", error=str(e), bucket=self.bucket, key=storage_key)
            raise IOError(f"Failed to download file from S3: {e}") from e

    async def delete(self, storage_key: str) -> None:
        """Delete file from S3."""
        try:
            self.s3_client.delete_object(Bucket=self.bucket, Key=storage_key)
            logger.info("File deleted from S3", bucket=self.bucket, key=storage_key)
        except ClientError as e:
            logger.error("S3 deletion failed", error=str(e), bucket=self.bucket, key=storage_key)
            raise IOError(f"Failed to delete file from S3: {e}") from e

    async def exists(self, storage_key: str) -> bool:
        """Check if file exists in S3."""
        try:
            self.s3_client.head_object(Bucket=self.bucket, Key=storage_key)
            return True
        except ClientError as e:
            if e.response["Error"]["Code"] == "404":
                return False
            logger.error("S3 exists check failed", error=str(e), bucket=self.bucket, key=storage_key)
            raise IOError(f"Failed to check file existence in S3: {e}") from e
