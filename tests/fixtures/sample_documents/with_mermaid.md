# Document with Mermaid Diagrams

This document contains Mermaid diagrams for testing diagram detection and extraction.

## Flow Diagram

```mermaid
graph TB
    A[Start] --> B{Is it working?}
    B -->|Yes| C[Great!]
    B -->|No| D[Debug]
    D --> A
    C --> E[End]
```

## Sequence Diagram

Here's a sequence diagram showing API authentication:

```mermaid
sequenceDiagram
    participant User
    participant API
    participant Database
    
    User->>API: Login Request
    API->>Database: Validate Credentials
    Database-->>API: User Data
    API-->>User: JWT Token
```

## Class Diagram

```mermaid
classDiagram
    class Document {
        +int id
        +string title
        +string content
        +parse()
        +save()
    }
    
    class MarkdownDocument {
        +string frontmatter
        +int heading_count
        +extractMetadata()
    }
    
    Document <|-- MarkdownDocument
```

## Regular Code Block

Not all code blocks are Mermaid diagrams:

```python
def process_mermaid(diagram_code):
    """Extract Mermaid diagram metadata."""
    return {
        'type': 'mermaid',
        'code': diagram_code
    }
```

## Testing Requirements

This document tests:
1. Detection of Mermaid code blocks (3 diagrams)
2. Extraction of diagram types (graph, sequence, class)
3. Differentiation from regular code blocks
4. Storage of diagram code for future rendering
