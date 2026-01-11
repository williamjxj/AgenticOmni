"""Mermaid diagram detection and extraction utilities.

Identifies and extracts Mermaid diagrams from markdown code blocks.
"""

from typing import Any

import marko
from marko.block import FencedCode


def extract_mermaid_diagrams(markdown_content: str) -> list[dict[str, Any]]:
    """Extract Mermaid diagrams from markdown content.
    
    Identifies code blocks with language 'mermaid' and extracts their content
    and diagram type.
    
    Args:
        markdown_content: The raw markdown content as a string.
        
    Returns:
        A list of dictionaries containing:
        - 'content': The Mermaid diagram code
        - 'diagram_type': The type of diagram (graph, sequenceDiagram, etc.)
        - 'position': The position index in the document
        
    Examples:
        >>> content = '''```mermaid
        ... graph TD
        ...     A-->B
        ... ```'''
        >>> diagrams = extract_mermaid_diagrams(content)
        >>> print(diagrams[0]['diagram_type'])
        "graph"
    """
    md = marko.Markdown()
    doc = md.parse(markdown_content)
    
    diagrams = []
    position = 0
    
    for child in doc.children:
        if isinstance(child, FencedCode):
            lang = getattr(child, "lang", "").lower().strip()
            
            if lang == "mermaid":
                code_content = child.children[0].children if child.children else ""
                
                # Extract diagram type from first line
                diagram_type = _detect_diagram_type(code_content)
                
                diagrams.append({
                    "content": code_content,
                    "diagram_type": diagram_type,
                    "position": position,
                })
                position += 1
    
    return diagrams


def _detect_diagram_type(mermaid_code: str) -> str:
    """Detect the type of Mermaid diagram from its code.
    
    Args:
        mermaid_code: The Mermaid diagram code.
        
    Returns:
        The diagram type (e.g., 'graph', 'sequenceDiagram', 'classDiagram').
        Returns 'unknown' if the type cannot be determined.
    """
    if not mermaid_code:
        return "unknown"
    
    # Get first non-empty line
    lines = [line.strip() for line in mermaid_code.split("\n") if line.strip()]
    if not lines:
        return "unknown"
    
    first_line = lines[0].lower()
    
    # Common Mermaid diagram types
    diagram_types = [
        "graph",
        "flowchart",
        "sequencediagram",
        "classdiagram",
        "statediagram",
        "erdiagram",
        "gantt",
        "pie",
        "journey",
        "gitgraph",
    ]
    
    for diagram_type in diagram_types:
        if first_line.startswith(diagram_type):
            return diagram_type
    
    return "unknown"


def count_mermaid_diagrams(markdown_content: str) -> int:
    """Count the number of Mermaid diagrams in markdown content.
    
    Args:
        markdown_content: The raw markdown content as a string.
        
    Returns:
        The count of Mermaid diagrams.
        
    Examples:
        >>> content = "# Doc\\n\\n```mermaid\\ngraph TD\\n```"
        >>> count = count_mermaid_diagrams(content)
        >>> print(count)
        1
    """
    diagrams = extract_mermaid_diagrams(markdown_content)
    return len(diagrams)
