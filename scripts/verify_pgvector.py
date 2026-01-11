#!/usr/bin/env python3
"""Verify pgvector extension is installed and available in PostgreSQL.

This script checks if the pgvector extension is properly installed and
can be enabled in the target database.

Usage:
    python scripts/verify_pgvector.py
    python scripts/verify_pgvector.py --database-url postgresql://...
"""

import argparse
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def verify_pgvector(database_url: str | None = None) -> bool:
    """Verify pgvector extension is available.

    Args:
        database_url: Optional PostgreSQL connection URL

    Returns:
        True if pgvector is available, False otherwise
    """
    try:
        import asyncpg
        import asyncio
    except ImportError as e:
        print("ERROR: asyncpg not installed")
        print("Run: pip install asyncpg>=0.29.0")
        return False

    # Load database URL from config if not provided
    if database_url is None:
        try:
            from config.settings import Settings
            settings = Settings()
            # Convert PostgresDsn to string and replace driver
            database_url = str(settings.database_url).replace(
                "postgresql+asyncpg://",
                "postgresql://"
            )
        except Exception as e:
            print(f"ERROR: Could not load database URL from settings: {e}")
            print("Provide --database-url argument")
            return False

    print("🔍 Verifying pgvector extension...")
    print(f"   Database: {database_url.split('@')[1] if '@' in database_url else 'N/A'}")
    print()

    async def check_pgvector():
        conn = None
        try:
            # Connect to database
            conn = await asyncpg.connect(database_url)
            print("✅ Database connection successful")

            # Check if pgvector extension is available
            result = await conn.fetchval(
                """
                SELECT EXISTS (
                    SELECT 1 
                    FROM pg_available_extensions 
                    WHERE name = 'vector'
                )
                """
            )

            if not result:
                print("❌ pgvector extension is NOT available")
                print()
                print("   To install pgvector:")
                print("   1. Follow: https://github.com/pgvector/pgvector#installation")
                print("   2. Then run: CREATE EXTENSION vector;")
                return False

            print("✅ pgvector extension is available")

            # Check if extension is already enabled
            enabled = await conn.fetchval(
                """
                SELECT EXISTS (
                    SELECT 1 
                    FROM pg_extension 
                    WHERE extname = 'vector'
                )
                """
            )

            if enabled:
                print("✅ pgvector extension is ENABLED")

                # Get version
                version = await conn.fetchval(
                    "SELECT extversion FROM pg_extension WHERE extname = 'vector'"
                )
                print(f"   Version: {version}")

                # Test vector operations
                try:
                    await conn.execute("SELECT '[1,2,3]'::vector")
                    print("✅ Vector operations working correctly")
                except Exception as e:
                    print(f"⚠️  Vector operations failed: {e}")
                    return False

            else:
                print("⚠️  pgvector extension is available but NOT ENABLED")
                print()
                print("   To enable, run as superuser:")
                print("   CREATE EXTENSION vector;")
                print()
                print("   Or use the migration script that will be created in Phase 2")
                return False

            return True

        except asyncpg.InvalidCatalogNameError:
            print("❌ Database does not exist")
            print(f"   Create it with: createdb {database_url.split('/')[-1]}")
            return False

        except asyncpg.InvalidPasswordError:
            print("❌ Invalid database credentials")
            return False

        except Exception as e:
            print(f"❌ Error: {e}")
            return False

        finally:
            if conn:
                await conn.close()

    # Run async check
    result = asyncio.run(check_pgvector())

    print()
    if result:
        print("=" * 70)
        print("✨ pgvector is ready for use!")
        print("=" * 70)
        print()
        print("   You can now:")
        print("   1. Run database migrations: alembic upgrade head")
        print("   2. Store vector embeddings in PostgreSQL")
        print("   3. Perform similarity searches with pgvector")
    else:
        print("=" * 70)
        print("❌ pgvector verification failed")
        print("=" * 70)
        print()
        print("   Follow the instructions above to install/enable pgvector")

    return result


def main() -> None:
    """Main entry point for pgvector verification script."""
    parser = argparse.ArgumentParser(
        description="Verify pgvector extension is available in PostgreSQL",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "--database-url",
        type=str,
        default=None,
        help="PostgreSQL connection URL (defaults to DATABASE_URL from .env)",
    )

    args = parser.parse_args()

    success = verify_pgvector(args.database_url)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
