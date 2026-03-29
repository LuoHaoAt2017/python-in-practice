#!/usr/bin/env python3
"""Test async connection."""

import asyncio
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from config.settings import settings

async def test_async_conn():
    """Test async connection with asyncpg."""
    print(f"Testing async connection...")
    print(f"DATABASE_URL_ASYNC: {settings.database_url_async}")

    try:
        # Try to create connection using asyncpg directly
        import asyncpg

        # Parse connection string
        # postgresql+asyncpg://postgres:LuoHao%40123@localhost:5432/sakila?server_settings=search_path=sakila
        url = settings.database_url_async

        # Extract connection parameters
        # Remove the asyncpg:// part and parse
        if url.startswith("postgresql+asyncpg://"):
            url = url.replace("postgresql+asyncpg://", "postgresql://")

        print(f"Parsed URL: {url}")

        # Connect with asyncpg
        conn = await asyncpg.connect(url)

        # Test query
        result = await conn.fetchval("SELECT COUNT(*) FROM actor;")
        print(f"Actor count: {result}")

        # Check search_path
        search_path = await conn.fetchval("SHOW search_path;")
        print(f"Search path: {search_path}")

        await conn.close()
        return True

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    try:
        success = asyncio.run(test_async_conn())
        if success:
            print("\n✅ Async connection test passed!")
            sys.exit(0)
        else:
            print("\n❌ Async connection test failed!")
            sys.exit(1)
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        sys.exit(1)