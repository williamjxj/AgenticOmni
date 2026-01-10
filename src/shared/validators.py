"""File validation utilities for document uploads."""

import hashlib
from pathlib import Path
from typing import Any

import magic


def detect_file_type(file_path: str) -> str:
    """Detect file MIME type using magic bytes inspection.
    
    Args:
        file_path: Path to the file to inspect
        
    Returns:
        Detected MIME type string (e.g., 'application/pdf')
        
    Raises:
        FileNotFoundError: If file does not exist
        
    Example:
        >>> mime_type = detect_file_type('/path/to/file.pdf')
        >>> print(mime_type)
        application/pdf
    """
    if not Path(file_path).exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    
    mime = magic.Magic(mime=True)
    return mime.from_file(file_path)


def validate_file_size(file_size: int, max_size_bytes: int) -> bool:
    """Validate file size is within allowed limit.
    
    Args:
        file_size: Size of file in bytes
        max_size_bytes: Maximum allowed size in bytes
        
    Returns:
        True if file size is valid, False otherwise
        
    Example:
        >>> is_valid = validate_file_size(5_000_000, 50_000_000)  # 5MB file, 50MB limit
        >>> print(is_valid)
        True
    """
    return 0 < file_size <= max_size_bytes


def validate_file_type(mime_type: str, allowed_types: list[str]) -> bool:
    """Validate file MIME type is in allowed list.
    
    Args:
        mime_type: Detected MIME type
        allowed_types: List of allowed MIME types
        
    Returns:
        True if file type is allowed, False otherwise
        
    Example:
        >>> is_valid = validate_file_type('application/pdf', ['application/pdf', 'text/plain'])
        >>> print(is_valid)
        True
    """
    return mime_type in allowed_types


def generate_content_hash(file_path: str) -> str:
    """Generate SHA-256 hash of file content for duplicate detection.
    
    Args:
        file_path: Path to the file
        
    Returns:
        Hexadecimal SHA-256 hash string (64 characters)
        
    Raises:
        FileNotFoundError: If file does not exist
        
    Example:
        >>> content_hash = generate_content_hash('/path/to/file.pdf')
        >>> print(len(content_hash))
        64
    """
    if not Path(file_path).exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    
    sha256_hash = hashlib.sha256()
    
    with Path(file_path).open("rb") as f:
        # Read file in chunks to handle large files efficiently
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    
    return sha256_hash.hexdigest()


async def scan_for_malware(file_path: str, clamav_host: str, clamav_port: int) -> tuple[bool, str | None]:
    """Scan file for malware using ClamAV.
    
    Args:
        file_path: Path to the file to scan
        clamav_host: ClamAV daemon host
        clamav_port: ClamAV daemon port
        
    Returns:
        Tuple of (is_clean, virus_name or None)
        
    Example:
        >>> is_clean, virus = await scan_for_malware('/path/to/file.pdf', 'localhost', 3310)
        >>> if not is_clean:
        ...     print(f"Malware detected: {virus}")
    """
    try:
        import clamd
        
        cd = clamd.ClamdNetworkSocket(host=clamav_host, port=clamav_port)
        result = cd.scan(file_path)
        
        if result is None:
            # File is clean
            return True, None
        
        # Malware detected
        file_result = result.get(file_path)
        if file_result and file_result[0] == "FOUND":
            return False, file_result[1]
        
        return True, None
        
    except Exception as e:
        # If ClamAV is unavailable, log warning and allow upload
        # (fail-open behavior - can be changed to fail-closed)
        import structlog
        
        logger = structlog.get_logger()
        logger.warning("ClamAV scan failed", error=str(e), file_path=file_path)
        return True, None


def get_mime_type_map() -> dict[str, str]:
    """Get mapping of file extensions to MIME types.
    
    Returns:
        Dictionary mapping extensions to MIME types
        
    Example:
        >>> mime_map = get_mime_type_map()
        >>> print(mime_map['pdf'])
        application/pdf
    """
    return {
        "pdf": "application/pdf",
        "docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "doc": "application/msword",
        "txt": "text/plain",
        "pptx": "application/vnd.openxmlformats-officedocument.presentationml.presentation",
        "xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    }


def get_supported_mime_types() -> list[str]:
    """Get list of supported MIME types for document parsing.
    
    Returns:
        List of supported MIME type strings
        
    Example:
        >>> supported = get_supported_mime_types()
        >>> print(supported)
        ['application/pdf', 'application/vnd...docx', 'text/plain']
    """
    return [
        "application/pdf",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "text/plain",
    ]


def validate_filename(filename: str) -> bool:
    """Validate filename does not contain path traversal characters.
    
    Args:
        filename: Original filename from upload
        
    Returns:
        True if filename is safe, False otherwise
        
    Example:
        >>> is_safe = validate_filename("document.pdf")
        >>> print(is_safe)
        True
        >>> is_safe = validate_filename("../../../etc/passwd")
        >>> print(is_safe)
        False
    """
    # Check for path traversal attempts
    dangerous_chars = ["../", "..\\", "/", "\\"]
    return not any(char in filename for char in dangerous_chars)
