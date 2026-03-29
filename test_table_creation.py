#!/usr/bin/env python3
"""Test table creation with current settings."""

import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from sqlalchemy import create_engine, text
from config.settings import settings
from models import Base

def test_table_creation():
    """Test if tables are created in correct schema."""
    print("Testing table creation...")
    print(f"DATABASE_URL: {settings.database_url}")

    # Create engine
    engine = create_engine(settings.database_url, echo=True)

    try:
        # First, drop any existing tables (in sakila schema)
        with engine.connect() as conn:
            # Get current search_path
            result = conn.execute(text("SHOW search_path;"))
            search_path = result.scalar()
            print(f"Current search_path: {search_path}")

            # List tables before creation
            result = conn.execute(text("""
                SELECT schemaname, tablename
                FROM pg_tables
                WHERE schemaname IN ('public', 'sakila')
                ORDER BY schemaname, tablename;
            """))
            print("Tables before creation:")
            for schema, table in result.fetchall():
                print(f"  - {schema}.{table}")

            # Drop tables in sakila schema if they exist
            print("\nDropping existing tables in sakila schema...")
            result = conn.execute(text("""
                SELECT tablename
                FROM pg_tables
                WHERE schemaname = 'sakila';
            """))
            tables = result.fetchall()
            for (table,) in tables:
                conn.execute(text(f'DROP TABLE IF EXISTS sakila."{table}" CASCADE;'))
                print(f"  - Dropped sakila.{table}")

            conn.commit()

        # Now create tables using SQLAlchemy
        print("\nCreating tables with SQLAlchemy...")
        Base.metadata.create_all(bind=engine)

        # Check where tables were created
        with engine.connect() as conn:
            result = conn.execute(text("""
                SELECT schemaname, tablename
                FROM pg_tables
                WHERE schemaname IN ('public', 'sakila')
                ORDER BY schemaname, tablename;
            """))
            print("\nTables after creation:")
            for schema, table in result.fetchall():
                print(f"  - {schema}.{table}")

            # Test if we can insert data
            print("\nTesting data insertion...")
            conn.execute(text("""
                INSERT INTO actor (first_name, last_name)
                VALUES ('Test', 'Actor');
            """))
            conn.commit()

            count = conn.execute(text("SELECT COUNT(*) FROM actor;")).scalar()
            print(f"Actor count after insertion: {count}")

            # Check which schema the actor table is in
            result = conn.execute(text("""
                SELECT schemaname
                FROM pg_tables
                WHERE tablename = 'actor';
            """))
            schemas = [row[0] for row in result.fetchall()]
            print(f"Actor table found in schemas: {schemas}")

            return True

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_table_creation()
    if success:
        print("\n✅ Table creation test passed!")
        sys.exit(0)
    else:
        print("\n❌ Table creation test failed!")
        sys.exit(1)