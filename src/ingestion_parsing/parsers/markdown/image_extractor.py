"""Image reference extraction utilities for markdown files.

Extracts image references from markdown content, including alt text, URLs,
and image type detection (local, base64, external).
"""

from pathlib import Path
from typing import Any

import marko
from marko.inline import Image


def extract_image_references(
    markdown_content: str, document_path: Path | None = None
) -> list[dict[str, Any]]:
    """Extract image references from markdown content.
    
    Traverses the marko AST to find Image nodes and extracts:
    - Image URL
    - Alt text
    - Image type (local path, base64, external URL)
    - Resolved path for local images
    
    Args:
        markdown_content: The raw markdown content as a string.
        document_path: Optional path to the markdown file for resolving relative paths.
        
    Returns:
        A list of dictionaries containing:
        - 'image_url': The original image URL/path
        - 'alt_text': The alt text (or None)
        - 'is_local_path': True if local file path
        - 'is_base64': True if base64 encoded
        - 'is_external_url': True if external URL
        - 'resolved_path': Resolved absolute path for local images (or None)
        - 'position': Position index in the document
        
    Examples:
        >>> content = "![Logo](./logo.png)"
        >>> images = extract_image_references(content, Path("doc.md"))
        >>> print(images[0]['is_local_path'])
        True
    """
    md = marko.Markdown()
    doc = md.parse(markdown_content)
    
    images = []
    position = 0
    
    def traverse(node: Any) -> None:
        """Recursively traverse AST to find Image nodes."""
        nonlocal position
        
        if isinstance(node, Image):
            image_url = node.dest
            alt_text = _extract_alt_text(node)
            
            # Detect image type
            is_base64 = _is_base64_image(image_url)
            is_external = _is_external_url(image_url)
            is_local = not is_base64 and not is_external
            
            # Resolve local paths
            resolved_path = None
            if is_local and document_path:
                resolved_path = _resolve_local_path(image_url, document_path)
            
            images.append({
                "image_url": image_url,
                "alt_text": alt_text,
                "is_local_path": is_local,
                "is_base64": is_base64,
                "is_external_url": is_external,
                "resolved_path": str(resolved_path) if resolved_path else None,
                "position": position,
            })
            position += 1
        
        # Traverse children
        if hasattr(node, "children") and node.children:
            for child in node.children:
                if hasattr(child, "children") or isinstance(child, Image):
                    traverse(child)
    
    traverse(doc)
    return images


def _extract_alt_text(image_node: Image) -> str | None:
    """Extract alt text from an Image node.
    
    Args:
        image_node: A marko Image AST node.
        
    Returns:
        The alt text as a string, or None if not present.
    """
    if not hasattr(image_node, "children") or not image_node.children:
        return None
    
    # Alt text is in the children as RawText
    alt_parts = []
    for child in image_node.children:
        if hasattr(child, "children"):
            alt_parts.append(str(child.children))
    
    alt_text = "".join(alt_parts).strip()
    return alt_text if alt_text else None


def _is_base64_image(url: str) -> bool:
    """Check if the URL is a base64 encoded image.
    
    Args:
        url: The image URL/path.
        
    Returns:
        True if base64 encoded, False otherwise.
    """
    return url.startswith("data:image/")


def _is_external_url(url: str) -> bool:
    """Check if the URL is an external URL.
    
    Args:
        url: The image URL/path.
        
    Returns:
        True if external URL (http/https), False otherwise.
    """
    return url.startswith("http://") or url.startswith("https://")


def _resolve_local_path(image_url: str, document_path: Path) -> Path | None:
    """Resolve a relative image path to an absolute path.
    
    Args:
        image_url: The relative image URL/path.
        document_path: The path to the markdown document.
        
    Returns:
        The resolved absolute path, or None if resolution fails.
    """
    try:
        # Get the directory containing the markdown file
        document_dir = document_path.parent
        
        # Resolve relative path
        image_path = (document_dir / image_url).resolve()
        
        return image_path
    except (ValueError, OSError):
        return None


def count_images(markdown_content: str) -> int:
    """Count the number of images in markdown content.
    
    Args:
        markdown_content: The raw markdown content as a string.
        
    Returns:
        The count of images.
        
    Examples:
        >>> content = "![Image 1](img1.png) ![Image 2](img2.png)"
        >>> count = count_images(content)
        >>> print(count)
        2
    """
    images = extract_image_references(markdown_content)
    return len(images)
