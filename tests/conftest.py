"""
Pytest configuration and fixtures for Sakila FastAPI tests.
"""
import asyncio
import pytest
from typing import AsyncGenerator, Generator
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

# Configure test database
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"
TEST_DATABASE_URL_SYNC = "sqlite:///:memory:"

from config.settings import settings


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
def sync_engine():
    """Create a synchronous SQLAlchemy engine for in-memory SQLite."""
    engine = create_engine(
        TEST_DATABASE_URL_SYNC,
        echo=False,
        connect_args={"check_same_thread": False},
    )
    yield engine
    engine.dispose()


@pytest.fixture(scope="session")
async def async_engine():
    """Create an asynchronous SQLAlchemy engine for in-memory SQLite."""
    engine = create_async_engine(
        TEST_DATABASE_URL,
        echo=False,
        connect_args={"check_same_thread": False},
    )
    yield engine
    await engine.dispose()


@pytest.fixture(scope="session")
def sync_session_factory(sync_engine):
    """Create a synchronous session factory."""
    from models import Base

    # Create all tables
    Base.metadata.create_all(bind=sync_engine)

    return sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=sync_engine,
    )


@pytest.fixture(scope="session")
async def async_session_factory(async_engine):
    """Create an asynchronous session factory."""
    from models import Base

    # Create all tables
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    return async_sessionmaker(
        async_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )


@pytest.fixture
def sync_db(sync_session_factory) -> Generator:
    """Provide a synchronous database session for tests."""
    db = sync_session_factory()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture
async def async_db(async_session_factory) -> AsyncGenerator:
    """Provide an asynchronous database session for tests."""
    async with async_session_factory() as session:
        try:
            yield session
        finally:
            await session.close()


@pytest.fixture
def test_settings():
    """Provide test settings."""
    from pydantic_settings import BaseSettings

    class TestSettings(BaseSettings):
        database_url: str = TEST_DATABASE_URL_SYNC
        database_url_async: str = TEST_DATABASE_URL
        debug: bool = True
        host: str = "0.0.0.0"
        port: int = 8000
        secret_key: str = "test-secret-key"
        api_prefix: str = "/api/v1"

    return TestSettings()


@pytest.fixture
async def test_client():
    """Create a test client for the FastAPI application."""
    from fastapi.testclient import TestClient
    from main import app

    with TestClient(app) as client:
        yield client


@pytest.fixture
async def test_data(async_db: AsyncSession):
    """Create test data for the database."""
    from models import (
        Language, Actor, Film, Category, FilmActor, FilmCategory,
        Country, City, Address, Store, Staff, Customer, Inventory, Rental
    )
    from datetime import datetime, timedelta

    # Create languages
    english = Language(name="English")
    async_db.add(english)
    await async_db.commit()
    await async_db.refresh(english)

    # Create actors
    actors = [
        Actor(first_name="John", last_name="Doe"),
        Actor(first_name="Jane", last_name="Smith"),
        Actor(first_name="Bob", last_name="Johnson"),
    ]
    async_db.add_all(actors)
    await async_db.commit()
    for actor in actors:
        await async_db.refresh(actor)

    # Create categories
    categories = [
        Category(name="Action"),
        Category(name="Comedy"),
        Category(name="Drama"),
    ]
    async_db.add_all(categories)
    await async_db.commit()
    for category in categories:
        await async_db.refresh(category)

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
    async_db.add_all(films)
    await async_db.commit()
    for film in films:
        await async_db.refresh(film)

    # Create film-actor relationships
    film_actors = [
        FilmActor(actor_id=actors[0].actor_id, film_id=films[0].film_id),
        FilmActor(actor_id=actors[1].actor_id, film_id=films[0].film_id),
        FilmActor(actor_id=actors[2].actor_id, film_id=films[1].film_id),
    ]
    async_db.add_all(film_actors)

    # Create film-category relationships
    film_categories = [
        FilmCategory(film_id=films[0].film_id, category_id=categories[0].category_id),
        FilmCategory(film_id=films[1].film_id, category_id=categories[1].category_id),
    ]
    async_db.add_all(film_categories)

    # Create country and city
    country = Country(country="United States")
    async_db.add(country)
    await async_db.commit()
    await async_db.refresh(country)

    city = City(city="New York", country_id=country.country_id)
    async_db.add(city)
    await async_db.commit()
    await async_db.refresh(city)

    # Create address
    address = Address(
        address="123 Main St",
        district="Manhattan",
        city_id=city.city_id,
        phone="555-1234",
    )
    async_db.add(address)
    await async_db.commit()
    await async_db.refresh(address)

    # Create store and staff
    staff = Staff(
        first_name="Store",
        last_name="Manager",
        address_id=address.address_id,
        email="manager@example.com",
        username="manager",
        active=True,
    )
    async_db.add(staff)
    await async_db.commit()
    await async_db.refresh(staff)

    store = Store(
        manager_staff_id=staff.staff_id,
        address_id=address.address_id,
    )
    async_db.add(store)
    await async_db.commit()
    await async_db.refresh(store)

    # Update staff with store_id
    staff.store_id = store.store_id
    await async_db.commit()
    await async_db.refresh(staff)

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
    async_db.add(customer)
    await async_db.commit()
    await async_db.refresh(customer)

    # Create inventory
    inventory = Inventory(
        film_id=films[0].film_id,
        store_id=store.store_id,
    )
    async_db.add(inventory)
    await async_db.commit()
    await async_db.refresh(inventory)

    # Create rental
    rental = Rental(
        rental_date=datetime.now() - timedelta(days=2),
        inventory_id=inventory.inventory_id,
        customer_id=customer.customer_id,
        staff_id=staff.staff_id,
        return_date=datetime.now() - timedelta(days=1),
    )
    async_db.add(rental)
    await async_db.commit()
    await async_db.refresh(rental)

    return {
        "english": english,
        "actors": actors,
        "films": films,
        "categories": categories,
        "country": country,
        "city": city,
        "address": address,
        "staff": staff,
        "store": store,
        "customer": customer,
        "inventory": inventory,
        "rental": rental,
    }