from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_, and_
from sqlalchemy.orm import selectinload

from models.film import Film
from schemas.film import FilmCreate, FilmUpdate


class FilmService:
    """Service for film-related operations."""

    @staticmethod
    async def get_films(
        db: AsyncSession,
        skip: int = 0,
        limit: int = 100,
        title: Optional[str] = None,
        release_year: Optional[int] = None,
        rating: Optional[str] = None,
        language_id: Optional[int] = None,
    ) -> List[Film]:
        """Get list of films with optional filtering and pagination."""
        query = select(Film).order_by(Film.title)

        filters = []
        if title:
            filters.append(Film.title.ilike(f"%{title}%"))
        if release_year:
            filters.append(Film.release_year == release_year)
        if rating:
            filters.append(Film.rating == rating)
        if language_id:
            filters.append(Film.language_id == language_id)

        if filters:
            query = query.where(and_(*filters))

        if limit > 0:
            query = query.offset(skip).limit(limit)

        result = await db.execute(query)
        return result.scalars().all()

    @staticmethod
    async def get_film_by_id(db: AsyncSession, film_id: int) -> Optional[Film]:
        """Get a film by ID."""
        query = select(Film).where(Film.film_id == film_id)
        result = await db.execute(query)
        return result.scalar_one_or_none()

    @staticmethod
    async def create_film(db: AsyncSession, film_data: FilmCreate) -> Film:
        """Create a new film."""
        film = Film(
            title=film_data.title,
            description=film_data.description,
            release_year=film_data.release_year,
            language_id=film_data.language_id,
            original_language_id=film_data.original_language_id,
            rental_duration=film_data.rental_duration,
            rental_rate=film_data.rental_rate,
            length=film_data.length,
            replacement_cost=film_data.replacement_cost,
            rating=film_data.rating,
            special_features=film_data.special_features,
        )
        db.add(film)
        await db.commit()
        await db.refresh(film)
        return film

    @staticmethod
    async def update_film(
        db: AsyncSession,
        film_id: int,
        film_data: FilmUpdate
    ) -> Optional[Film]:
        """Update an existing film."""
        film = await FilmService.get_film_by_id(db, film_id)
        if not film:
            return None

        update_data = film_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(film, field, value)

        await db.commit()
        await db.refresh(film)
        return film

    @staticmethod
    async def delete_film(db: AsyncSession, film_id: int) -> bool:
        """Delete a film."""
        film = await FilmService.get_film_by_id(db, film_id)
        if not film:
            return False

        await db.delete(film)
        await db.commit()
        return True

    @staticmethod
    async def get_films_count(
        db: AsyncSession,
        title: Optional[str] = None,
        release_year: Optional[int] = None,
        rating: Optional[str] = None,
        language_id: Optional[int] = None,
    ) -> int:
        """Get total count of films with optional filtering."""
        query = select(func.count(Film.film_id))

        filters = []
        if title:
            filters.append(Film.title.ilike(f"%{title}%"))
        if release_year:
            filters.append(Film.release_year == release_year)
        if rating:
            filters.append(Film.rating == rating)
        if language_id:
            filters.append(Film.language_id == language_id)

        if filters:
            query = query.where(and_(*filters))

        result = await db.execute(query)
        return result.scalar() or 0

    @staticmethod
    async def get_film_with_actors(db: AsyncSession, film_id: int) -> Optional[Film]:
        """Get a film with its actors."""
        query = (
            select(Film)
            .where(Film.film_id == film_id)
            .options(selectinload(Film.film_actors).selectinload("actor"))
        )
        result = await db.execute(query)
        return result.scalar_one_or_none()

    @staticmethod
    async def get_film_with_categories(db: AsyncSession, film_id: int) -> Optional[Film]:
        """Get a film with its categories."""
        query = (
            select(Film)
            .where(Film.film_id == film_id)
            .options(selectinload(Film.film_categories).selectinload("category"))
        )
        result = await db.execute(query)
        return result.scalar_one_or_none()