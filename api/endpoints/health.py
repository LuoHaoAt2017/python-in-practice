from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from config.database import get_async_db

router = APIRouter()


@router.get("/")
async def health():
    """Basic health check."""
    return {"status": "healthy"}


@router.get("/db")
async def db_health(db: AsyncSession = Depends(get_async_db)):
    """Database health check."""
    try:
        result = await db.execute(text("SELECT 1"))
        result.scalar()
        return {"database": "healthy"}
    except Exception as e:
        return {"database": "unhealthy", "error": str(e)}