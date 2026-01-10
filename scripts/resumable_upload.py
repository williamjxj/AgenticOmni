#!/usr/bin/env python3
"""Helper script for uploading large files using resumable upload API.

This script demonstrates how to upload large files (> 50MB) using chunked uploads
that can be resumed if interrupted.
"""

import argparse
import hashlib
import os
import sys
import time
from pathlib import Path
from typing import Any

import requests


class ResumableUploader:
    """Client for uploading large files with resume support."""

    def __init__(
        self,
        api_base: str = "http://localhost:8000/api/v1",
        chunk_size: int = 10_000_000,  # 10MB
        max_retries: int = 3,
    ) -> None:
        """Initialize uploader.
        
        Args:
            api_base: API base URL
            chunk_size: Chunk size in bytes (1MB - 100MB)
            max_retries: Maximum retry attempts per chunk
        """
        self.api_base = api_base
        self.chunk_size = chunk_size
        self.max_retries = max_retries

    def upload_file(
        self,
        file_path: str,
        tenant_id: int,
        user_id: int,
        compute_hash: bool = True,
    ) -> dict[str, Any]:
        """Upload a large file using resumable upload API.
        
        Args:
            file_path: Path to file to upload
            tenant_id: Tenant ID
            user_id: User ID
            compute_hash: Whether to compute and verify file hash
            
        Returns:
            Dictionary with upload result
            
        Raises:
            requests.exceptions.RequestException: On upload failure
        """
        file_path_obj = Path(file_path)
        if not file_path_obj.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        file_size = file_path_obj.stat().st_size
        filename = file_path_obj.name
        
        print(f"📁 Uploading: {filename}")
        print(f"📊 Size: {file_size:,} bytes ({file_size / 1024 / 1024:.2f} MB)")
        
        # Compute file hash if requested
        content_hash = None
        if compute_hash:
            print("🔐 Computing file hash...")
            content_hash = self._compute_hash(file_path)
            print(f"✅ SHA-256: {content_hash}")
        
        # Step 1: Initialize session
        print("\n🔄 Initializing upload session...")
        session = self._init_session(
            filename=filename,
            file_size=file_size,
            tenant_id=tenant_id,
            user_id=user_id,
            content_hash=content_hash,
        )
        
        session_id = session["session_id"]
        total_chunks = session["total_chunks"]
        
        print(f"✅ Session created: {session_id}")
        print(f"📦 Total chunks: {total_chunks}")
        print(f"⏰ Expires: {session['expires_at']}")
        
        # Step 2: Upload chunks
        print("\n⬆️  Uploading chunks...")
        start_time = time.time()
        
        with open(file_path, "rb") as f:
            for chunk_num in range(total_chunks):
                chunk_start = chunk_num * self.chunk_size
                chunk_end = min(chunk_start + self.chunk_size, file_size) - 1
                
                # Read chunk
                f.seek(chunk_start)
                chunk_data = f.read(self.chunk_size)
                
                # Upload with retry
                result = self._upload_chunk_with_retry(
                    session_id=session_id,
                    chunk_data=chunk_data,
                    start=chunk_start,
                    end=chunk_end,
                    total_size=file_size,
                    chunk_num=chunk_num,
                    total_chunks=total_chunks,
                )
                
                # Show progress
                progress = result["progress_percent"]
                elapsed = time.time() - start_time
                uploaded = result["uploaded_bytes"]
                speed = uploaded / elapsed / 1024 / 1024  # MB/s
                
                print(
                    f"  Chunk {chunk_num + 1}/{total_chunks}: "
                    f"{progress:.1f}% | "
                    f"{speed:.2f} MB/s | "
                    f"Status: {result['status']}"
                )
        
        elapsed_total = time.time() - start_time
        avg_speed = file_size / elapsed_total / 1024 / 1024
        
        print(f"\n✅ Upload complete!")
        print(f"⏱️  Time: {elapsed_total:.1f}s")
        print(f"🚀 Average speed: {avg_speed:.2f} MB/s")
        
        if "document_id" in result:
            print(f"📄 Document ID: {result['document_id']}")
            print(f"⚙️  Job ID: {result['job_id']}")
        
        return result

    def _init_session(
        self,
        filename: str,
        file_size: int,
        tenant_id: int,
        user_id: int,
        content_hash: str | None = None,
    ) -> dict[str, Any]:
        """Initialize resumable upload session."""
        response = requests.post(
            f"{self.api_base}/documents/upload/resumable",
            json={
                "filename": filename,
                "file_size": file_size,
                "tenant_id": tenant_id,
                "user_id": user_id,
                "chunk_size": self.chunk_size,
                "content_hash": content_hash,
            },
        )
        response.raise_for_status()
        return response.json()

    def _upload_chunk_with_retry(
        self,
        session_id: str,
        chunk_data: bytes,
        start: int,
        end: int,
        total_size: int,
        chunk_num: int,
        total_chunks: int,
    ) -> dict[str, Any]:
        """Upload a chunk with automatic retry on failure."""
        for attempt in range(self.max_retries):
            try:
                response = requests.patch(
                    f"{self.api_base}/documents/upload/resumable/{session_id}",
                    headers={
                        "Content-Range": f"bytes {start}-{end}/{total_size}",
                        "Content-Type": "application/octet-stream",
                    },
                    data=chunk_data,
                    timeout=60,
                )
                response.raise_for_status()
                return response.json()
                
            except requests.exceptions.RequestException as e:
                if attempt < self.max_retries - 1:
                    wait_time = 2 ** attempt  # Exponential backoff
                    print(
                        f"    ❌ Chunk {chunk_num + 1}/{total_chunks} failed "
                        f"(attempt {attempt + 1}/{self.max_retries}), "
                        f"retrying in {wait_time}s..."
                    )
                    time.sleep(wait_time)
                else:
                    print(f"    ❌ Chunk {chunk_num + 1}/{total_chunks} failed after {self.max_retries} attempts")
                    raise

    def _compute_hash(self, file_path: str) -> str:
        """Compute SHA-256 hash of file."""
        hasher = hashlib.sha256()
        with open(file_path, "rb") as f:
            while chunk := f.read(8192):
                hasher.update(chunk)
        return hasher.hexdigest()

    def check_progress(self, session_id: str) -> dict[str, Any]:
        """Check upload progress for a session.
        
        Args:
            session_id: Session identifier
            
        Returns:
            Dictionary with session progress
        """
        response = requests.get(
            f"{self.api_base}/documents/upload/resumable/{session_id}"
        )
        response.raise_for_status()
        return response.json()

    def cancel_upload(self, session_id: str) -> dict[str, Any]:
        """Cancel an upload session.
        
        Args:
            session_id: Session identifier
            
        Returns:
            Dictionary with cancellation result
        """
        response = requests.delete(
            f"{self.api_base}/documents/upload/resumable/{session_id}"
        )
        response.raise_for_status()
        return response.json()


def main() -> None:
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Upload large files using resumable upload API"
    )
    parser.add_argument(
        "file_path",
        help="Path to file to upload",
    )
    parser.add_argument(
        "--api-base",
        default="http://localhost:8000/api/v1",
        help="API base URL (default: http://localhost:8000/api/v1)",
    )
    parser.add_argument(
        "--tenant-id",
        type=int,
        default=1,
        help="Tenant ID (default: 1)",
    )
    parser.add_argument(
        "--user-id",
        type=int,
        default=1,
        help="User ID (default: 1)",
    )
    parser.add_argument(
        "--chunk-size",
        type=int,
        default=10_000_000,
        help="Chunk size in bytes (default: 10MB)",
    )
    parser.add_argument(
        "--no-hash",
        action="store_true",
        help="Skip hash computation",
    )
    
    args = parser.parse_args()
    
    # Validate chunk size
    if args.chunk_size < 1_000_000 or args.chunk_size > 100_000_000:
        print("❌ Chunk size must be between 1MB and 100MB")
        sys.exit(1)
    
    # Create uploader
    uploader = ResumableUploader(
        api_base=args.api_base,
        chunk_size=args.chunk_size,
    )
    
    # Upload file
    try:
        result = uploader.upload_file(
            file_path=args.file_path,
            tenant_id=args.tenant_id,
            user_id=args.user_id,
            compute_hash=not args.no_hash,
        )
        
        print("\n🎉 Upload successful!")
        sys.exit(0)
        
    except FileNotFoundError as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)
        
    except requests.exceptions.RequestException as e:
        print(f"\n❌ Upload failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
