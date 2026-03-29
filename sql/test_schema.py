#!/usr/bin/env python3
"""Test script to verify database schema settings."""

import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from sqlalchemy import text, create_engine
from config.settings import settings

def test_schema():
    """Test if the database connection uses the correct schema."""
    print("Testing database schema settings...")
    print(f"DATABASE_URL: {settings.database_url}")

    # Create engine
    engine = create_engine(settings.database_url)

    try:
        with engine.connect() as conn:
            # Test 1: Check current search_path
            result = conn.execute(text("SHOW search_path;"))
            search_path = result.scalar()
            print(f"Current search_path: {search_path}")

            # Test 2: Try to query actor table
            result = conn.execute(text("SELECT COUNT(*) FROM actor;"))
            count = result.scalar()
            print(f"Actor count: {count}")

            # Test 3: Check which schema the table is in
            result = conn.execute(text("""
                SELECT schemaname, tablename
                FROM pg_tables
                WHERE tablename = 'actor'
                ORDER BY schemaname;
            """))
            tables = result.fetchall()
            print("Actor tables found:")
            for schema, table in tables:
                print(f"  - {schema}.{table}")

            # Test 4: Check if we can query sakila.actor directly
            result = conn.execute(text("SELECT COUNT(*) FROM sakila.actor;"))
            sakila_count = result.scalar()
            print(f"Actor count in sakila schema: {sakila_count}")

            return True

    except Exception as e:
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    success = test_schema()
    sys.exit(0 if success else 1)