from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import sessionmaker

from config.settings import settings

# Import Base from models to ensure all models use the same base class
from models.base import Base


# Synchronous engine for migrations and scripts
engine = create_engine(
    settings.database_url,
    echo=settings.debug,
    pool_pre_ping=True,
    pool_recycle=300,
)

# Asynchronous engine for FastAPI endpoints
async_engine = create_async_engine(
    settings.database_url_async,
    echo=settings.debug,
    pool_pre_ping=True,
    pool_recycle=300,
    future=True,
    connect_args={
        "server_settings": {"search_path": "sakila"}
    }
)

# Synchronous session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)

# Asynchronous session factory
AsyncSessionLocal = async_sessionmaker(
    async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


def get_db():
    """Dependency for synchronous database sessions."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


async def get_async_db():
    """Dependency for asynchronous database sessions."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()