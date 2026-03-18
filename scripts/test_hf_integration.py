#!/usr/bin/env python3
"""Quick test script for HuggingFace datasets integration.

This script tests the basic functionality without requiring the full
API server to be running.
"""

import asyncio
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))


async def test_hf_loader():
    """Test HuggingFace dataset loader."""
    print("=" * 60)
    print("Testing HuggingFace Dataset Loader")
    print("=" * 60)
    
    from src.ingestion_parsing.services.hf_dataset_loader import HFDatasetLoader
    
    # Initialize loader
    print("\n1. Initializing HFDatasetLoader...")
    loader = HFDatasetLoader()
    print("   ✓ Loader initialized")
    
    # Test SQuAD dataset loading (small sample)
    print("\n2. Loading SQuAD dataset (limit=5)...")
    try:
        records = loader.load_squad_dataset(split="train", limit=5)
        print(f"   ✓ Loaded {len(records)} records")
        
        # Display first record
        if records:
            record = records[0]
            print(f"\n   Sample Record:")
            print(f"   - Text length: {len(record['text'])} chars")
            print(f"   - Content hash: {record['content_hash'][:16]}...")
            print(f"   - Source: {record['source']}")
            print(f"   - Metadata: {record['metadata']['title']}")
            print(f"\n   First 200 chars of text:")
            print(f"   {record['text'][:200]}...")
        
    except Exception as e:
        print(f"   ✗ Error: {e}")
        return False
    
    # Test dataset validation
    print("\n3. Testing dataset validation...")
    try:
        is_accessible = loader.validate_dataset_access("rajpurkar/squad")
        if is_accessible:
            print("   ✓ Dataset 'rajpurkar/squad' is accessible")
        else:
            print("   ✗ Dataset 'rajpurkar/squad' is not accessible")
    except Exception as e:
        print(f"   ✗ Error: {e}")
        return False
    
    print("\n" + "=" * 60)
    print("All tests passed! ✓")
    print("=" * 60)
    return True


async def test_chunking():
    """Test chunking service with sample text."""
    print("\n" + "=" * 60)
    print("Testing Chunking Service")
    print("=" * 60)
    
    from src.ingestion_parsing.services.chunking_service import ChunkingService
    
    # Initialize chunker
    print("\n1. Initializing ChunkingService...")
    chunker = ChunkingService(
        chunk_size_tokens=512,
        chunk_overlap_tokens=50,
    )
    print("   ✓ Chunker initialized")
    
    # Sample text
    sample_text = """
    Machine learning is a subset of artificial intelligence that focuses on 
    enabling computers to learn from data without explicit programming. It has 
    revolutionized many fields including natural language processing, computer 
    vision, and robotics. The core idea is to develop algorithms that can 
    identify patterns in data and make predictions or decisions based on those 
    patterns. Deep learning, a subset of machine learning, uses neural networks 
    with multiple layers to learn hierarchical representations of data.
    """ * 3  # Repeat to make it longer
    
    print(f"\n2. Chunking sample text ({len(sample_text)} chars)...")
    try:
        chunks = chunker.chunk_document(sample_text)
        print(f"   ✓ Created {len(chunks)} chunks")
        
        for i, chunk in enumerate(chunks):
            print(f"   - Chunk {i}: {chunk.token_count} tokens, type={chunk.chunk_type}")
        
    except Exception as e:
        print(f"   ✗ Error: {e}")
        return False
    
    print("\n" + "=" * 60)
    print("Chunking test passed! ✓")
    print("=" * 60)
    return True


async def main():
    """Run all tests."""
    print("\n" + "=" * 60)
    print("HuggingFace Datasets Integration Test Suite")
    print("=" * 60)
    
    # Test 1: HF Loader
    loader_ok = await test_hf_loader()
    
    # Test 2: Chunking
    chunking_ok = await test_chunking()
    
    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    print(f"HF Loader:  {'✓ PASS' if loader_ok else '✗ FAIL'}")
    print(f"Chunking:   {'✓ PASS' if chunking_ok else '✗ FAIL'}")
    print("=" * 60)
    
    if loader_ok and chunking_ok:
        print("\n✓ All integration tests passed!")
        print("\nNext steps:")
        print("1. Start the API server: uvicorn src.api.main:app --reload")
        print("2. Visit: http://localhost:8000/api/v1/docs")
        print("3. Try the /datasets/import endpoint")
        return 0
    else:
        print("\n✗ Some tests failed. Check the errors above.")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
