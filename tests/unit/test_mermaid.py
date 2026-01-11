"""Unit tests for Mermaid diagram extraction.

Tests Mermaid code block detection and diagram type identification.
User Story 4: Handle Special Markdown Content (Priority: P3)
"""

from pathlib import Path

import pytest

from src.ingestion_parsing.parsers.markdown.mermaid import extract_mermaid_diagrams


def test_extract_mermaid_diagrams_basic() -> None:
    """Test basic Mermaid diagram detection.
    
    User Story 4, Task T091
    """
    # Arrange
    content = """# Diagram

```mermaid
graph TD
    A[Start] --> B[End]
```

Some text.
"""
    
    # Act
    diagrams = extract_mermaid_diagrams(content)
    
    # Assert
    assert len(diagrams) == 1
    assert "graph" in diagrams[0]["content"].lower()
    assert "A[Start]" in diagrams[0]["content"]


def test_extract_mermaid_diagram_types() -> None:
    """Test extraction of different Mermaid diagram types.
    
    User Story 4, Task T092
    """
    # Arrange
    content = """# Diagrams

```mermaid
graph LR
    A --> B
```

```mermaid
sequenceDiagram
    Alice->>Bob: Hello
    Bob->>Alice: Hi
```

```mermaid
classDiagram
    class Animal
    Animal : +int age
```

```mermaid
erDiagram
    CUSTOMER ||--o{ ORDER : places
```
"""
    
    # Act
    diagrams = extract_mermaid_diagrams(content)
    
    # Assert
    assert len(diagrams) == 4
    
    diagram_types = [d["diagram_type"] for d in diagrams]
    assert "graph" in diagram_types
    assert "sequencediagram" in diagram_types
    assert "classdiagram" in diagram_types
    assert "erdiagram" in diagram_types


def test_extract_mermaid_no_diagrams() -> None:
    """Test extraction when no Mermaid diagrams exist.
    
    User Story 4, Task T091
    """
    # Arrange
    content = """# Document

```python
def hello():
    pass
```

No Mermaid here.
"""
    
    # Act
    diagrams = extract_mermaid_diagrams(content)
    
    # Assert
    assert len(diagrams) == 0


def test_extract_mermaid_multiple_diagrams() -> None:
    """Test extraction of multiple Mermaid diagrams.
    
    User Story 4, Task T091
    """
    # Arrange
    content = """# Diagrams

## Flow

```mermaid
graph TD
    Start --> End
```

## Sequence

```mermaid
sequenceDiagram
    A->>B: Message
```

## State

```mermaid
stateDiagram-v2
    [*] --> Active
```
"""
    
    # Act
    diagrams = extract_mermaid_diagrams(content)
    
    # Assert
    assert len(diagrams) == 3


def test_extract_mermaid_with_comments() -> None:
    """Test Mermaid extraction with comments in diagram code.
    
    User Story 4, Task T091
    """
    # Arrange
    content = """# Diagram

```mermaid
graph TD
    %% This is a comment
    A[Start] --> B[Process]
    B --> C[End]
    %% Another comment
```
"""
    
    # Act
    diagrams = extract_mermaid_diagrams(content)
    
    # Assert
    assert len(diagrams) == 1
    assert "%% This is a comment" in diagrams[0]["content"]


def test_extract_mermaid_malformed_graceful() -> None:
    """Test graceful handling of malformed Mermaid syntax.
    
    User Story 4, Task T106
    """
    # Arrange
    content = """# Diagram

```mermaid
graph TD
    A[Unclosed bracket
    B --> C
```
"""
    
    # Act - should not crash
    diagrams = extract_mermaid_diagrams(content)
    
    # Assert - should still extract the code
    assert len(diagrams) == 1
    assert "A[Unclosed bracket" in diagrams[0]["content"]


def test_extract_mermaid_empty_code_block() -> None:
    """Test handling of empty Mermaid code blocks.
    
    User Story 4, Task T091
    """
    # Arrange
    content = """# Diagram

```mermaid
```

Text after.
"""
    
    # Act
    diagrams = extract_mermaid_diagrams(content)
    
    # Assert - empty diagram should still be detected
    assert len(diagrams) == 1
    assert diagrams[0]["content"].strip() == ""


def test_extract_mermaid_preserves_indentation() -> None:
    """Test that Mermaid code indentation is preserved.
    
    User Story 4, Task T091
    """
    # Arrange
    content = """# Diagram

```mermaid
graph TD
    subgraph cluster
        A --> B
        B --> C
    end
```
"""
    
    # Act
    diagrams = extract_mermaid_diagrams(content)
    
    # Assert
    assert len(diagrams) == 1
    # Check that indentation is preserved
    assert "subgraph cluster" in diagrams[0]["content"]
    assert "A --> B" in diagrams[0]["content"]


def test_extract_mermaid_diagram_type_detection() -> None:
    """Test accurate diagram type detection from first line.
    
    User Story 4, Task T098
    """
    # Arrange
    test_cases = [
        ("graph TD", "graph"),
        ("graph LR", "graph"),
        ("sequenceDiagram", "sequencediagram"),
        ("classDiagram", "classdiagram"),
        ("stateDiagram-v2", "statediagram"),
        ("erDiagram", "erdiagram"),
        ("journey", "journey"),
        ("gantt", "gantt"),
        ("pie", "pie"),
        ("flowchart TD", "flowchart"),
    ]
    
    for first_line, expected_type in test_cases:
        content = f"""# Diagram

```mermaid
{first_line}
    A --> B
```
"""
        
        # Act
        diagrams = extract_mermaid_diagrams(content)
        
        # Assert
        assert len(diagrams) == 1
        assert diagrams[0]["diagram_type"] == expected_type
