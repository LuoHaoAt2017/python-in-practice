#!/usr/bin/env python3
"""Test if API can access data in sakila schema."""

import sys
import asyncio
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy import select
from sqlalchemy.orm import sessionmaker
from config.settings import settings

from models.actor import Actor
from models.film import Film
from models.language import Language

async def test_api_data():
    """Test async database access."""
    print("Testing API data access...")
    print(f"DATABASE_URL_ASYNC: {settings.database_url_async}")

    # Create async engine
    engine = create_async_engine(
        settings.database_url_async,
        echo=True,  # Show SQL for debugging
    )

    async with AsyncSession(engine) as session:
        # Test 1: Query actors
        print("\n1. Testing actor query...")
        stmt = select(Actor).order_by(Actor.last_name, Actor.first_name).limit(5)
        result = await session.execute(stmt)
        actors = result.scalars().all()

        print(f"Found {len(actors)} actors:")
        for actor in actors:
            print(f"  - {actor.first_name} {actor.last_name} (ID: {actor.actor_id})")

        # Test 2: Query films
        print("\n2. Testing film query...")
        stmt = select(Film).order_by(Film.title).limit(5)
        result = await session.execute(stmt)
        films = result.scalars().all()

        print(f"Found {len(films)} films:")
        for film in films:
            print(f"  - {film.title} (ID: {film.film_id})")

        # Test 3: Query count
        print("\n3. Testing counts...")
        stmt = select(Actor.actor_id)
        result = await session.execute(stmt)
        all_actors = result.scalars().all()
        print(f"Total actors in database: {len(all_actors)}")

        stmt = select(Film.film_id)
        result = await session.execute(stmt)
        all_films = result.scalars().all()
        print(f"Total films in database: {len(all_films)}")

        return True

if __name__ == "__main__":
    try:
        asyncio.run(test_api_data())
        print("\n✅ All tests passed!")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        sys.exit(1)