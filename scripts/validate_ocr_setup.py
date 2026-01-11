#!/usr/bin/env python3
"""Validate OCR setup and dependencies.

Feature: 004-ocr-embedding-pipeline

Quick script to check if all OCR dependencies are properly installed
and configured.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def validate_dependencies() -> dict[str, bool]:
    """Validate all required dependencies.

    Returns:
        Dictionary with dependency check results
    """
    results = {}

    # Check core dependencies
    try:
        import sqlalchemy
        results["sqlalchemy"] = True
    except ImportError:
        results["sqlalchemy"] = False

    try:
        import pydantic
        results["pydantic"] = True
    except ImportError:
        results["pydantic"] = False

    try:
        import fastapi
        results["fastapi"] = True
    except ImportError:
        results["fastapi"] = False

    # Check OCR dependencies
    try:
        import paddleocr
        results["paddleocr"] = True
    except ImportError:
        results["paddleocr"] = False

    try:
        import pytesseract
        results["pytesseract"] = True
    except ImportError:
        results["pytesseract"] = False

    try:
        import pdf2image
        results["pdf2image"] = True
    except ImportError:
        results["pdf2image"] = False

    # Check embedding dependencies
    try:
        from sentence_transformers import SentenceTransformer
        results["sentence_transformers"] = True
    except ImportError:
        results["sentence_transformers"] = False

    try:
        import langdetect
        results["langdetect"] = True
    except ImportError:
        results["langdetect"] = False

    # Check pgvector
    try:
        from pgvector.sqlalchemy import Vector
        results["pgvector"] = True
    except ImportError:
        results["pgvector"] = False

    return results


def validate_modules() -> dict[str, bool]:
    """Validate that project modules can be imported.

    Returns:
        Dictionary with module check results
    """
    results = {}

    try:
        from src.ingestion_parsing.parsers.ocr.base import BaseOcrEngine
        results["ocr_base"] = True
    except ImportError:
        results["ocr_base"] = False

    try:
        from src.ingestion_parsing.parsers.ocr.paddleocr_engine import PaddleOcrEngine
        results["paddleocr_engine"] = True
    except ImportError:
        results["paddleocr_engine"] = False

    try:
        from src.ingestion_parsing.services.ocr_service import OcrService
        results["ocr_service"] = True
    except ImportError:
        results["ocr_service"] = False

    try:
        from src.api.routes.ocr import router
        results["ocr_api"] = True
    except ImportError:
        results["ocr_api"] = False

    try:
        from src.storage_indexing.models.extracted_text import ExtractedText
        results["extracted_text_model"] = True
    except ImportError:
        results["extracted_text_model"] = False

    return results


def main() -> None:
    """Main validation function."""
    print("=" * 70)
    print("🔍 OCR Feature Setup Validation")
    print("=" * 70)
    print()

    # Validate dependencies
    print("📦 Checking Dependencies...")
    print("-" * 70)
    dep_results = validate_dependencies()

    all_deps_ok = True
    for dep, status in dep_results.items():
        status_icon = "✅" if status else "❌"
        print(f"  {status_icon} {dep:<30} {'OK' if status else 'MISSING'}")
        if not status:
            all_deps_ok = False

    print()

    # Validate modules
    print("🔧 Checking Project Modules...")
    print("-" * 70)
    module_results = validate_modules()

    all_modules_ok = True
    for module, status in module_results.items():
        status_icon = "✅" if status else "❌"
        print(f"  {status_icon} {module:<30} {'OK' if status else 'FAILED'}")
        if not status:
            all_modules_ok = False

    print()
    print("=" * 70)

    # Summary
    if all_deps_ok and all_modules_ok:
        print("✨ All checks passed! OCR feature is ready to use.")
        print()
        print("Next steps:")
        print("  1. Run migrations: alembic upgrade head")
        print("  2. Download models: python scripts/download_models.py")
        print("  3. Verify pgvector: python scripts/verify_pgvector.py")
        print("  4. Start API: uvicorn src.api.main:app --reload")
        sys.exit(0)
    else:
        print("❌ Some checks failed. Please fix the issues above.")
        print()

        if not all_deps_ok:
            print("Missing dependencies can be installed with:")
            print("  pip install -r requirements.txt")
            print()

        if not all_modules_ok:
            print("Module import failures may indicate:")
            print("  - Code errors (check linter output)")
            print("  - Missing __init__.py files")
            print("  - Circular import issues")

        sys.exit(1)


if __name__ == "__main__":
    main()
