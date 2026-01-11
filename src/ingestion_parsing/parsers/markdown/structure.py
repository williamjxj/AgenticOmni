"""Structural element identification utilities for markdown.

Identifies and extracts structural elements from markdown content:
- Headings (H1-H6)
- Code blocks
- Lists (ordered and unordered)
- Tables
- Blockquotes
"""

from typing import Any

import marko
from marko.block import (
    Quote,
    FencedCode,
    Heading,
    List as MarkdownList,
    ThematicBreak,
)
from marko.ext.gfm.elements import Table


def extract_structural_elements(markdown_content: str) -> list[dict[str, Any]]:
    """Extract structural elements from markdown content.
    
    Traverses the marko AST and identifies all structural elements with
    their type, content preview, and position.
    
    Args:
        markdown_content: The raw markdown content as a string.
        
    Returns:
        A list of dictionaries containing:
        - 'type': Element type (heading, code_block, list, table, blockquote, hr)
        - 'level': For headings, the level (1-6)
        - 'content_preview': First 100 chars of content
        - 'language': For code blocks, the language specifier
        - 'position': Position index in the document
        
    Examples:
        >>> content = "# Title\\n\\n## Subtitle\\n\\n- List item"
        >>> elements = extract_structural_elements(content)
        >>> print(elements[0]['type'])
        "heading"
    """
    md = marko.Markdown(extensions=["gfm"])
    doc = md.parse(markdown_content)
    
    elements = []
    position = 0
    
    for child in doc.children:
        element = _identify_element(child, position)
        if element:
            elements.append(element)
            position += 1
    
    return elements


def _identify_element(node: Any, position: int) -> dict[str, Any] | None:
    """Identify a single structural element from an AST node.
    
    Args:
        node: A marko AST node.
        position: The position index.
        
    Returns:
        A dictionary with element information, or None if not a structural element.
    """
    if isinstance(node, Heading):
        return {
            "type": "heading",
            "level": node.level,
            "content_preview": _get_text_preview(node),
            "position": position,
        }
    
    if isinstance(node, FencedCode):
        lang = getattr(node, "lang", "").strip() if hasattr(node, "lang") else ""
        return {
            "type": "code_block",
            "language": lang or "plain",
            "content_preview": _get_text_preview(node),
            "position": position,
        }
    
    if isinstance(node, MarkdownList):
        list_type = "ordered" if node.ordered else "unordered"
        return {
            "type": "list",
            "list_type": list_type,
            "content_preview": _get_text_preview(node),
            "position": position,
        }
    
    if isinstance(node, Table):
        return {
            "type": "table",
            "content_preview": _get_text_preview(node),
            "position": position,
        }
    
    if isinstance(node, Quote):
        return {
            "type": "blockquote",
            "content_preview": _get_text_preview(node),
            "position": position,
        }
    
    if isinstance(node, ThematicBreak):
        return {
            "type": "hr",
            "position": position,
        }
    
    return None


def _get_text_preview(node: Any, max_length: int = 100) -> str:
    """Extract a text preview from an AST node.
    
    Args:
        node: A marko AST node.
        max_length: Maximum length of the preview.
        
    Returns:
        A preview string truncated to max_length.
    """
    try:
        # Try to get text content
        if hasattr(node, "children") and node.children:
            text_parts = []
            _collect_text(node, text_parts)
            full_text = "".join(text_parts).strip()
            
            if len(full_text) > max_length:
                return full_text[:max_length] + "..."
            return full_text
    except Exception:
        pass
    
    return ""


def _collect_text(node: Any, text_parts: list[str]) -> None:
    """Recursively collect text from an AST node.
    
    Args:
        node: A marko AST node.
        text_parts: A list to append text parts to.
    """
    if isinstance(node, str):
        text_parts.append(node)
        return
    
    if hasattr(node, "children"):
        if isinstance(node.children, str):
            text_parts.append(node.children)
        elif isinstance(node.children, list):
            for child in node.children:
                _collect_text(child, text_parts)
        else:
            _collect_text(node.children, text_parts)


def count_structural_elements(markdown_content: str) -> dict[str, int]:
    """Count structural elements by type.
    
    Args:
        markdown_content: The raw markdown content as a string.
        
    Returns:
        A dictionary with counts for each element type:
        - 'heading_count'
        - 'code_block_count'
        - 'list_count'
        - 'table_count'
        - 'blockquote_count'
        - 'hr_count'
        
    Examples:
        >>> content = "# Title\\n\\n```python\\ncode\\n```\\n\\n- item"
        >>> counts = count_structural_elements(content)
        >>> print(counts['heading_count'])
        1
    """
    elements = extract_structural_elements(markdown_content)
    
    counts = {
        "heading_count": 0,
        "code_block_count": 0,
        "list_count": 0,
        "table_count": 0,
        "blockquote_count": 0,
        "hr_count": 0,
    }
    
    for element in elements:
        element_type = element["type"]
        if element_type == "heading":
            counts["heading_count"] += 1
        elif element_type == "code_block":
            counts["code_block_count"] += 1
        elif element_type == "list":
            counts["list_count"] += 1
        elif element_type == "table":
            counts["table_count"] += 1
        elif element_type == "blockquote":
            counts["blockquote_count"] += 1
        elif element_type == "hr":
            counts["hr_count"] += 1
    
    return counts
