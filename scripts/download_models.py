#!/usr/bin/env python3
"""Download and cache embedding models for offline use.

This script pre-downloads the embedding models used by the OCR and Embedding Pipeline
feature to avoid delays during first-time usage.

Usage:
    python scripts/download_models.py
    python scripts/download_models.py --model multilingual-e5-large
    python scripts/download_models.py --cache-dir /path/to/cache
"""

import argparse
import sys
from pathlib import Path
from typing import Optional

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def download_embedding_model(
    model_name: str = "intfloat/multilingual-e5-base",
    cache_dir: Optional[str] = None,
) -> None:
    """Download and cache an embedding model from HuggingFace.

    Args:
        model_name: HuggingFace model identifier
        cache_dir: Optional custom cache directory

    Raises:
        ImportError: If sentence-transformers is not installed
        Exception: If model download fails
    """
    try:
        from sentence_transformers import SentenceTransformer
    except ImportError as e:
        print("ERROR: sentence-transformers not installed")
        print("Run: pip install sentence-transformers>=2.3.0")
        raise e

    print(f"📥 Downloading embedding model: {model_name}")
    print(f"   Cache directory: {cache_dir or 'default (~/.cache/huggingface)'}")
    print()

    try:
        # Download model (will cache automatically)
        model = SentenceTransformer(model_name, cache_folder=cache_dir)

        # Get model info
        embedding_dim = model.get_sentence_embedding_dimension()
        max_seq_length = model.max_seq_length

        print("✅ Model downloaded successfully!")
        print()
        print(f"   Model: {model_name}")
        print(f"   Embedding dimensions: {embedding_dim}")
        print(f"   Max sequence length: {max_seq_length} tokens")
        print()
        print("   The model is now cached and ready for use.")

    except Exception as e:
        print(f"❌ Failed to download model: {e}")
        raise


def download_paddleocr_models() -> None:
    """Download and cache PaddleOCR models.

    PaddleOCR models are downloaded automatically on first use,
    but we can trigger the download here for offline preparation.
    """
    try:
        from paddleocr import PaddleOCR
    except ImportError as e:
        print("WARNING: paddleocr not installed")
        print("Run: pip install paddleocr>=2.7.0 paddlepaddle-gpu>=2.6.0")
        print("Skipping PaddleOCR model download...")
        return

    print("📥 Downloading PaddleOCR models...")
    print("   This may take a few minutes...")
    print()

    try:
        # Initialize PaddleOCR (downloads models on first use)
        # English and Chinese models
        ocr_en = PaddleOCR(lang="en", use_gpu=False, show_log=False)
        ocr_zh = PaddleOCR(lang="ch", use_gpu=False, show_log=False)

        print("✅ PaddleOCR models downloaded successfully!")
        print()
        print("   English model: Ready")
        print("   Chinese model: Ready")
        print()

    except Exception as e:
        print(f"❌ Failed to download PaddleOCR models: {e}")
        print("   Models will be downloaded automatically on first use.")


def main() -> None:
    """Main entry point for model download script."""
    parser = argparse.ArgumentParser(
        description="Download and cache models for OCR and Embedding Pipeline",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "--model",
        type=str,
        default="intfloat/multilingual-e5-base",
        help="Embedding model to download (default: intfloat/multilingual-e5-base)",
    )

    parser.add_argument(
        "--cache-dir",
        type=str,
        default=None,
        help="Custom cache directory for models",
    )

    parser.add_argument(
        "--skip-paddleocr",
        action="store_true",
        help="Skip PaddleOCR model download",
    )

    parser.add_argument(
        "--embedding-only",
        action="store_true",
        help="Download only embedding models (skip OCR)",
    )

    args = parser.parse_args()

    print("=" * 70)
    print("Model Download Script - OCR and Embedding Pipeline")
    print("=" * 70)
    print()

    # Download embedding model
    try:
        download_embedding_model(args.model, args.cache_dir)
    except Exception as e:
        print(f"Failed to download embedding model: {e}")
        sys.exit(1)

    # Download PaddleOCR models (unless skipped)
    if not args.skip_paddleocr and not args.embedding_only:
        print()
        print("-" * 70)
        print()
        try:
            download_paddleocr_models()
        except Exception as e:
            print(f"Warning: PaddleOCR download failed: {e}")
            print("Continuing anyway...")

    print()
    print("=" * 70)
    print("✨ Model download complete!")
    print("=" * 70)
    print()
    print("Next steps:")
    print("  1. Verify models are cached: ls ~/.cache/huggingface/")
    print("  2. Run the application: uvicorn src.api.main:app --reload")
    print("  3. Test OCR: POST /api/v1/documents/{id}/ocr")
    print("  4. Test embeddings: POST /api/v1/documents/{id}/embeddings")
    print()


if __name__ == "__main__":
    main()
