# Contributing to AgenticOmni

Thank you for your interest in contributing to AgenticOmni! This document provides guidelines and workflows for development.

## Development Workflow

### 1. Environment Setup

```bash
# Clone the repository
git clone <repository-url>
cd ai-edocuments

# Set up Python virtual environment
python3.12 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -e .

# Set up environment variables
cp .env.example .env
# Edit .env with your configuration

# Start Docker services
docker-compose up -d

# Run database migrations
./scripts/setup_db.sh

# Start backend server
./scripts/run_dev.sh
```

### 2. Frontend Development

```bash
# Install frontend dependencies
cd frontend
npm install

# Start development server
npm run dev

# Run linter
npm run lint

# Build for production
npm run build
```

### 3. Running Tests

```bash
# Run all tests with coverage
./scripts/run_tests.sh

# Run specific test file
pytest tests/unit/test_config.py -v

# Run tests with specific markers
pytest -m "not slow"
```

## Code Standards

### Python Code Style

We follow PEP 8 with additional conventions:

- **Formatting**: Use `ruff` for code formatting
- **Type Hints**: All functions must have type annotations
- **Docstrings**: Use Google-style docstrings for all public functions and classes
- **Line Length**: Maximum 100 characters (enforced by ruff)

```python
def process_document(
    document_id: int,
    tenant_id: int,
    *,
    force: bool = False
) -> ProcessingResult:
    """Process a document through the ETL pipeline.

    Args:
        document_id: Unique identifier for the document
        tenant_id: Tenant ID for multi-tenancy isolation
        force: Force reprocessing even if already complete

    Returns:
        ProcessingResult: Result containing status and metadata

    Raises:
        DocumentNotFoundError: If document_id doesn't exist
        ProcessingError: If processing fails

    Example:
        >>> result = process_document(123, tenant_id=1)
        >>> print(result.status)
        ProcessingStatus.COMPLETED
    """
    # Implementation
```

### TypeScript/React Code Style

- **Formatting**: Follows Next.js and Prettier conventions
- **Components**: Use functional components with TypeScript
- **Naming**: PascalCase for components, camelCase for functions/variables
- **File Structure**: One component per file

```typescript
/**
 * DocumentCard Component
 * 
 * Displays document metadata in a card format.
 */
interface DocumentCardProps {
  document: Document;
  onSelect?: (id: string) => void;
}

export function DocumentCard({ document, onSelect }: DocumentCardProps) {
  // Implementation
}
```

## Git Workflow

### Branch Naming

- `feature/` - New features
- `fix/` - Bug fixes
- `docs/` - Documentation updates
- `refactor/` - Code refactoring
- `test/` - Test improvements

Examples:
- `feature/add-pdf-parsing`
- `fix/health-check-timeout`
- `docs/update-api-guide`

### Commit Messages

Follow [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

**Examples:**

```
feat(ingestion): add support for PPTX files

Implement PPTX parsing using python-pptx library.
Extracts text, images, and slide metadata.

Closes #123
```

```
fix(api): resolve health check database timeout

Increase connection timeout from 5s to 10s to prevent
false negatives during high load.

Fixes #456
```

### Pull Request Process

1. **Create Feature Branch**
   ```bash
   git checkout -b feature/my-new-feature
   ```

2. **Make Changes**
   - Write code following style guidelines
   - Add tests for new functionality
   - Update documentation as needed

3. **Run Quality Checks**
   ```bash
   # Python
   ruff check src/ tests/ config/
   ruff format src/ tests/ config/
   mypy src/ config/
   pytest

   # Frontend
   cd frontend
   npm run lint
   npm run build
   ```

4. **Commit Changes**
   ```bash
   git add .
   git commit -m "feat(module): add new feature"
   ```

5. **Push and Create PR**
   ```bash
   git push origin feature/my-new-feature
   ```
   - Create PR on GitHub/GitLab
   - Fill out PR template
   - Request review from maintainers

6. **Address Review Comments**
   - Make requested changes
   - Push additional commits
   - Mark conversations as resolved

7. **Merge**
   - Squash and merge for single-commit features
   - Rebase and merge for multi-commit features
   - Delete branch after merge

## Testing Guidelines

### Unit Tests

- Test individual functions and classes in isolation
- Mock external dependencies (database, APIs, file system)
- Aim for 80%+ code coverage
- Place in `tests/unit/`

```python
def test_tenant_model_creation(db_session):
    """Verify a Tenant can be created and retrieved."""
    tenant = Tenant(name="Test Tenant", domain="test-domain", status="active")
    db_session.add(tenant)
    await db_session.commit()
    
    assert tenant.tenant_id is not None
    assert tenant.name == "Test Tenant"
```

### Integration Tests

- Test interactions between components
- Use test database (not production!)
- Test API endpoints end-to-end
- Place in `tests/integration/`

```python
async def test_health_endpoint_returns_200(test_client):
    """Verify the health endpoint returns a 200 OK status."""
    response = await test_client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"
```

### Test Fixtures

- Define shared fixtures in `tests/conftest.py`
- Use `pytest.fixture` for reusable test data
- Clean up resources after tests

## Documentation

### Code Documentation

- All public functions, classes, and modules must have docstrings
- Use Google-style docstrings
- Include type hints in function signatures
- Provide usage examples for complex functions

### Project Documentation

- Update `README.md` for user-facing changes
- Update `docs/` for detailed technical documentation
- Use Markdown for all documentation
- Include diagrams using Mermaid when helpful

### Documentation Version Control

All documentation in `docs/` uses semantic versioning:

```yaml
---
title: "Document Title"
version: "1.0.0"
date: "2026-01-09"
authors: ["Your Name"]
status: "active"
---
```

See `docs/VERSIONING_GUIDE.md` for details.

## Database Migrations

### Creating Migrations

```bash
# Auto-generate migration from model changes
alembic revision --autogenerate -m "Add new_column to users"

# Review generated migration file
# Edit if needed (e.g., add data migrations)

# Apply migration
alembic upgrade head
```

### Migration Best Practices

- One migration per logical change
- Always test migrations on development database first
- Include both `upgrade()` and `downgrade()` functions
- Add comments for complex migrations
- Never modify existing migrations after they're merged

## Security

### Reporting Security Issues

- **DO NOT** open public issues for security vulnerabilities
- Email security@yourcompany.com with details
- Include steps to reproduce and potential impact
- We will respond within 48 hours

### Security Best Practices

- Never commit secrets to git (use environment variables)
- Use parameterized queries (SQLAlchemy handles this)
- Validate all user inputs
- Follow OWASP Top 10 guidelines
- Run `bandit` security linter on Python code

## Code Review Guidelines

### As a Reviewer

- Be constructive and respectful
- Focus on code quality, not personal preferences
- Check for:
  - Correctness and logic errors
  - Test coverage
  - Documentation completeness
  - Security vulnerabilities
  - Performance issues

### As an Author

- Keep PRs small and focused (< 400 lines)
- Respond to feedback promptly
- Don't take criticism personally
- Explain your decisions when needed

## Questions or Issues?

- **Bug Reports**: Open an issue with reproduction steps
- **Feature Requests**: Open an issue with use case and rationale
- **Questions**: Use GitHub Discussions or Slack channel
- **Urgent Issues**: Contact maintainers directly

## License

By contributing to AgenticOmni, you agree that your contributions will be licensed under the project's license.

---

Thank you for contributing to AgenticOmni! 🚀
