#!/usr/bin/env python3
"""Test document parsers with sample files.

This script tests the document parsing functionality for PDF, DOCX, and TXT files.
"""

import argparse
import sys
from pathlib import Path
from typing import Any

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.ingestion_parsing.parsers.parser_factory import ParserFactory
from src.shared.validators import detect_file_type


def test_parser(file_path: str) -> None:
    """Test document parser on a file.
    
    Args:
        file_path: Path to file to parse
    """
    file_path_obj = Path(file_path)
    
    if not file_path_obj.exists():
        print(f"❌ File not found: {file_path}")
        sys.exit(1)
    
    print(f"📄 Testing parser for: {file_path_obj.name}")
    print(f"📊 File size: {file_path_obj.stat().st_size:,} bytes")
    
    # Detect file type
    print("\n🔍 Detecting file type...")
    mime_type = detect_file_type(file_path)
    print(f"✅ MIME type: {mime_type}")
    
    # Get parser
    print("\n🔧 Getting parser...")
    try:
        parser = ParserFactory.get_parser(mime_type)
        print(f"✅ Parser: {parser.__class__.__name__}")
    except ValueError as e:
        print(f"❌ Parser error: {e}")
        sys.exit(1)
    
    # Parse document
    print("\n📖 Parsing document...")
    try:
        result = parser.parse(file_path)
        
        print(f"✅ Parsing successful!")
        print(f"\n📝 Results:")
        print(f"  - Text length: {len(result.text):,} characters")
        print(f"  - Word count: ~{len(result.text.split()):,} words")
        
        if result.metadata:
            print(f"\n📋 Metadata:")
            for key, value in result.metadata.items():
                if value:
                    print(f"  - {key}: {value}")
        
        # Show text preview
        preview_length = 200
        if len(result.text) > preview_length:
            print(f"\n📄 Text preview (first {preview_length} chars):")
            print(f"  {result.text[:preview_length]}...")
        else:
            print(f"\n📄 Full text:")
            print(f"  {result.text}")
        
        print(f"\n✅ Test completed successfully!")
        
    except Exception as e:
        print(f"❌ Parsing failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


def test_all_formats() -> None:
    """Test all supported document formats."""
    test_dir = Path(__file__).parent.parent / "tests" / "fixtures" / "sample_documents"
    
    if not test_dir.exists():
        print(f"❌ Test directory not found: {test_dir}")
        sys.exit(1)
    
    print("🧪 Testing all supported formats\n")
    print("=" * 60)
    
    test_files = {
        "PDF": test_dir / "sample.pdf",
        "DOCX": test_dir / "sample.docx",
        "TXT": test_dir / "sample.txt",
    }
    
    results: dict[str, bool] = {}
    
    for format_name, file_path in test_files.items():
        print(f"\n{'=' * 60}")
        print(f"Testing {format_name}")
        print('=' * 60)
        
        if not file_path.exists():
            print(f"⚠️  Skipping {format_name}: file not found ({file_path.name})")
            results[format_name] = False
            continue
        
        try:
            test_parser(str(file_path))
            results[format_name] = True
        except SystemExit:
            results[format_name] = False
    
    # Summary
    print(f"\n{'=' * 60}")
    print("📊 Test Summary")
    print('=' * 60)
    
    for format_name, success in results.items():
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"  {format_name}: {status}")
    
    passed = sum(results.values())
    total = len(results)
    
    print(f"\nTotal: {passed}/{total} passed")
    
    if passed == total:
        print("\n🎉 All tests passed!")
        sys.exit(0)
    else:
        print(f"\n❌ {total - passed} test(s) failed")
        sys.exit(1)


def benchmark_parser(file_path: str, iterations: int = 5) -> None:
    """Benchmark parser performance.
    
    Args:
        file_path: Path to file to parse
        iterations: Number of iterations to run
    """
    import time
    
    file_path_obj = Path(file_path)
    
    if not file_path_obj.exists():
        print(f"❌ File not found: {file_path}")
        sys.exit(1)
    
    print(f"⚡ Benchmarking parser for: {file_path_obj.name}")
    print(f"📊 File size: {file_path_obj.stat().st_size:,} bytes")
    print(f"🔄 Iterations: {iterations}")
    
    # Detect file type and get parser
    mime_type = detect_file_type(file_path)
    parser = ParserFactory.get_parser(mime_type)
    
    print(f"\n🔧 Parser: {parser.__class__.__name__}")
    print("\n⏱️  Running benchmark...")
    
    times = []
    
    for i in range(iterations):
        start = time.time()
        result = parser.parse(file_path)
        elapsed = time.time() - start
        times.append(elapsed)
        print(f"  Iteration {i + 1}: {elapsed:.3f}s ({len(result.text):,} chars)")
    
    # Calculate statistics
    avg_time = sum(times) / len(times)
    min_time = min(times)
    max_time = max(times)
    
    print(f"\n📊 Benchmark Results:")
    print(f"  Average: {avg_time:.3f}s")
    print(f"  Min: {min_time:.3f}s")
    print(f"  Max: {max_time:.3f}s")
    print(f"  Throughput: {file_path_obj.stat().st_size / avg_time / 1024 / 1024:.2f} MB/s")


def main() -> None:
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Test document parsers"
    )
    parser.add_argument(
        "file_path",
        nargs="?",
        help="Path to file to parse (omit to test all formats)",
    )
    parser.add_argument(
        "--benchmark",
        action="store_true",
        help="Run benchmark instead of test",
    )
    parser.add_argument(
        "--iterations",
        type=int,
        default=5,
        help="Number of benchmark iterations (default: 5)",
    )
    
    args = parser.parse_args()
    
    if args.file_path:
        if args.benchmark:
            benchmark_parser(args.file_path, args.iterations)
        else:
            test_parser(args.file_path)
    else:
        if args.benchmark:
            print("❌ Benchmark requires a file path")
            sys.exit(1)
        test_all_formats()


if __name__ == "__main__":
    main()
