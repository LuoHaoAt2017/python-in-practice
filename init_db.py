#!/usr/bin/env python3
"""
Database initialization script for Sakila PostgreSQL database.

This script:
1. Creates the database if it doesn't exist
2. Creates tables using SQLAlchemy models
3. Loads sample data from Sakila SQL files if available
4. Sets up test data for development

Requirements:
- PostgreSQL must be installed and running
- psycopg2 or psycopg2-binary must be installed
"""

import os
import sys
import argparse
import logging
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def check_postgres_connection():
    """Check if PostgreSQL is available."""
    try:
        import psycopg2
        from config.settings import settings

        # Extract connection parameters from DATABASE_URL
        # Format: postgresql://user:password@host:port/database
        db_url = settings.database_url

        # Try to connect to PostgreSQL server (without specific database)
        # For simplicity, we'll try to connect to the default database first
        conn = psycopg2.connect(
            host="localhost",
            port=5432,
            user="root",
            password="LuoHao@123",
            database="sakila",  # Connect to default database first
        )
        conn.close()
        logger.info("✅ PostgreSQL connection successful")
        return True
    except Exception as e:
        logger.error(f"❌ PostgreSQL connection failed: {e}")
        logger.info("Make sure PostgreSQL is running and credentials are correct")
        logger.info(
            "Default credentials: user=postgres, password=postgres, host=localhost, port=5432"
        )
        return False


def create_database():
    """Create the sakila database if it doesn't exist."""
    try:
        import psycopg2

        # Connect to default database
        conn = psycopg2.connect(
            host="localhost",
            port=5432,
            user="postgres",
            password="postgres",
            database="postgres",
        )
        conn.autocommit = True
        cursor = conn.cursor()

        # Check if database exists
        cursor.execute("SELECT 1 FROM pg_database WHERE datname = 'sakila'")
        exists = cursor.fetchone()

        if not exists:
            cursor.execute("CREATE DATABASE sakila")
            logger.info("✅ Created 'sakila' database")
        else:
            logger.info("✅ Database 'sakila' already exists")

        cursor.close()
        conn.close()
        return True

    except Exception as e:
        logger.error(f"❌ Failed to create database: {e}")
        return False


def create_tables():
    """Create tables using SQLAlchemy models."""
    try:
        from sqlalchemy import create_engine
        from config.settings import settings
        from models import Base

        # Use synchronous engine for table creation
        engine = create_engine(settings.database_url)

        # Create all tables
        Base.metadata.create_all(bind=engine)

        logger.info("✅ Created all tables")
        return True

    except Exception as e:
        logger.error(f"❌ Failed to create tables: {e}")
        return False


def load_sample_data():
    """Load sample data if SQL files are available."""
    # Check for Sakila SQL files in common locations
    possible_locations = [
        project_root / "sakila-schema.sql",
        project_root / "sakila-data.sql",
        project_root / "sakila.sql",
        project_root / "sql" / "sakila-schema.sql",
        project_root / "sql" / "sakila-data.sql",
        project_root / "data" / "sakila-schema.sql",
        project_root / "data" / "sakila-data.sql",
    ]

    schema_file = None
    data_file = None

    for location in possible_locations:
        if location.name.endswith("-schema.sql") and location.exists():
            schema_file = location
        elif location.name.endswith("-data.sql") and location.exists():
            data_file = location

    if schema_file or data_file:
        try:
            import psycopg2
            from config.settings import settings

            conn = psycopg2.connect(settings.database_url)
            cursor = conn.cursor()

            if schema_file:
                logger.info(f"Loading schema from {schema_file}")
                with open(schema_file, "r", encoding="utf-8") as f:
                    cursor.execute(f.read())
                logger.info("✅ Loaded schema")

            if data_file:
                logger.info(f"Loading data from {data_file}")
                with open(data_file, "r", encoding="utf-8") as f:
                    cursor.execute(f.read())
                logger.info("✅ Loaded sample data")

            conn.commit()
            cursor.close()
            conn.close()
            return True

        except Exception as e:
            logger.error(f"❌ Failed to load sample data: {e}")
            return False
    else:
        logger.info("ℹ️  No Sakila SQL files found. Creating test data instead.")
        return create_test_data()


def create_test_data():
    """Create minimal test data for development."""
    try:
        from sqlalchemy.orm import Session
        from config.database import engine
        from models import (
            Language,
            Actor,
            Film,
            Category,
            FilmActor,
            FilmCategory,
            Country,
            City,
            Address,
            Store,
            Staff,
            Customer,
            Inventory,
            Rental,
        )
        from datetime import datetime, timedelta

        with Session(engine) as session:
            # Create languages
            english = Language(name="English")
            french = Language(name="French")
            session.add_all([english, french])
            session.commit()

            # Create actors
            actors = [
                Actor(first_name="John", last_name="Doe"),
                Actor(first_name="Jane", last_name="Smith"),
                Actor(first_name="Bob", last_name="Johnson"),
            ]
            session.add_all(actors)
            session.commit()

            # Create categories
            categories = [
                Category(name="Action"),
                Category(name="Comedy"),
                Category(name="Drama"),
            ]
            session.add_all(categories)
            session.commit()

            # Create films
            films = [
                Film(
                    title="The Great Adventure",
                    description="An epic adventure film",
                    release_year=2023,
                    language_id=english.language_id,
                    rental_duration=3,
                    rental_rate=4.99,
                    length=120,
                    replacement_cost=19.99,
                    rating="PG-13",
                ),
                Film(
                    title="Laugh Out Loud",
                    description="A hilarious comedy",
                    release_year=2022,
                    language_id=english.language_id,
                    rental_duration=5,
                    rental_rate=3.99,
                    length=95,
                    replacement_cost=14.99,
                    rating="PG",
                ),
            ]
            session.add_all(films)
            session.commit()

            # Create film-actor relationships
            film_actors = [
                FilmActor(actor_id=actors[0].actor_id, film_id=films[0].film_id),
                FilmActor(actor_id=actors[1].actor_id, film_id=films[0].film_id),
                FilmActor(actor_id=actors[2].actor_id, film_id=films[1].film_id),
            ]
            session.add_all(film_actors)

            # Create film-category relationships
            film_categories = [
                FilmCategory(
                    film_id=films[0].film_id, category_id=categories[0].category_id
                ),
                FilmCategory(
                    film_id=films[1].film_id, category_id=categories[1].category_id
                ),
            ]
            session.add_all(film_categories)

            # Create country and city
            country = Country(country="United States")
            session.add(country)
            session.commit()

            city = City(city="New York", country_id=country.country_id)
            session.add(city)
            session.commit()

            # Create address
            address = Address(
                address="123 Main St",
                district="Manhattan",
                city_id=city.city_id,
                phone="555-1234",
            )
            session.add(address)
            session.commit()

            # Create store and staff
            staff = Staff(
                first_name="Store",
                last_name="Manager",
                address_id=address.address_id,
                email="manager@example.com",
                username="manager",
                active=True,
            )
            session.add(staff)
            session.commit()

            store = Store(
                manager_staff_id=staff.staff_id,
                address_id=address.address_id,
            )
            session.add(store)
            session.commit()

            # Update staff with store_id
            staff.store_id = store.store_id
            session.commit()

            # Create customer
            customer = Customer(
                store_id=store.store_id,
                first_name="Alice",
                last_name="Brown",
                email="alice@example.com",
                address_id=address.address_id,
                activebool=True,
                create_date=datetime.now(),
                active=1,
            )
            session.add(customer)
            session.commit()

            # Create inventory
            inventory = Inventory(
                film_id=films[0].film_id,
                store_id=store.store_id,
            )
            session.add(inventory)
            session.commit()

            # Create rental
            rental = Rental(
                rental_date=datetime.now() - timedelta(days=2),
                inventory_id=inventory.inventory_id,
                customer_id=customer.customer_id,
                staff_id=staff.staff_id,
                return_date=datetime.now() - timedelta(days=1),
            )
            session.add(rental)

            session.commit()

            logger.info("✅ Created test data")
            logger.info(f"   - Actors: {len(actors)}")
            logger.info(f"   - Films: {len(films)}")
            logger.info(f"   - Categories: {len(categories)}")
            logger.info(f"   - Customers: 1")
            logger.info(f"   - Rentals: 1")

            return True

    except Exception as e:
        logger.error(f"❌ Failed to create test data: {e}")
        return False


def main():
    """Main function to initialize the database."""
    parser = argparse.ArgumentParser(
        description="Initialize Sakila PostgreSQL database"
    )
    parser.add_argument(
        "--skip-check", action="store_true", help="Skip PostgreSQL connection check"
    )
    parser.add_argument(
        "--skip-create", action="store_true", help="Skip database creation"
    )
    parser.add_argument(
        "--skip-tables", action="store_true", help="Skip table creation"
    )
    parser.add_argument("--skip-data", action="store_true", help="Skip data loading")
    parser.add_argument("--force", action="store_true", help="Force re-initialization")

    args = parser.parse_args()

    logger.info("Starting Sakila database initialization...")

    # Step 1: Check PostgreSQL connection
    if not args.skip_check:
        logger.info("Step 1: Checking PostgreSQL connection...")
        if not check_postgres_connection():
            sys.exit(1)
    else:
        logger.info("ℹ️  Skipping PostgreSQL connection check")

    # Step 2: Create database
    if not args.skip_create:
        logger.info("Step 2: Creating database...")
        if not create_database():
            sys.exit(1)
    else:
        logger.info("ℹ️  Skipping database creation")

    # Step 3: Create tables
    if not args.skip_tables:
        logger.info("Step 3: Creating tables...")
        if not create_tables():
            sys.exit(1)
    else:
        logger.info("ℹ️  Skipping table creation")

    # Step 4: Load data
    if not args.skip_data:
        logger.info("Step 4: Loading data...")
        if not load_sample_data():
            logger.warning("⚠️  Data loading had issues, but continuing...")
    else:
        logger.info("ℹ️  Skipping data loading")

    logger.info("✨ Database initialization complete!")
    logger.info("\nNext steps:")
    logger.info("1. Start the FastAPI server: python main.py")
    logger.info("2. Access the API documentation: http://localhost:8000/docs")
    logger.info("3. Test the API endpoints")


if __name__ == "__main__":
    main()
