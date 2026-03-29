from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload

from models.actor import Actor
from schemas.actor import ActorCreate, ActorUpdate


class ActorService:
    """Service for actor-related operations."""

    @staticmethod
    async def get_actors(
        db: AsyncSession,
        skip: int = 0,
        limit: int = 100,
        name: Optional[str] = None
    ) -> List[Actor]:
        """Get list of actors with optional filtering and pagination."""
        query = select(Actor).order_by(Actor.last_name, Actor.first_name)

        if name:
            query = query.where(
                (Actor.first_name.ilike(f"%{name}%")) |
                (Actor.last_name.ilike(f"%{name}%"))
            )

        if limit > 0:
            query = query.offset(skip).limit(limit)

        result = await db.execute(query)
        return result.scalars().all()

    @staticmethod
    async def get_actor_by_id(db: AsyncSession, actor_id: int) -> Optional[Actor]:
        """Get an actor by ID."""
        query = select(Actor).where(Actor.actor_id == actor_id)
        result = await db.execute(query)
        return result.scalar_one_or_none()

    @staticmethod
    async def create_actor(db: AsyncSession, actor_data: ActorCreate) -> Actor:
        """Create a new actor."""
        actor = Actor(
            first_name=actor_data.first_name,
            last_name=actor_data.last_name,
        )
        db.add(actor)
        await db.commit()
        await db.refresh(actor)
        return actor

    @staticmethod
    async def update_actor(
        db: AsyncSession,
        actor_id: int,
        actor_data: ActorUpdate
    ) -> Optional[Actor]:
        """Update an existing actor."""
        actor = await ActorService.get_actor_by_id(db, actor_id)
        if not actor:
            return None

        update_data = actor_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(actor, field, value)

        await db.commit()
        await db.refresh(actor)
        return actor

    @staticmethod
    async def delete_actor(db: AsyncSession, actor_id: int) -> bool:
        """Delete an actor."""
        actor = await ActorService.get_actor_by_id(db, actor_id)
        if not actor:
            return False

        await db.delete(actor)
        await db.commit()
        return True

    @staticmethod
    async def get_actors_count(db: AsyncSession, name: Optional[str] = None) -> int:
        """Get total count of actors with optional filtering."""
        query = select(func.count(Actor.actor_id))

        if name:
            query = query.where(
                (Actor.first_name.ilike(f"%{name}%")) |
                (Actor.last_name.ilike(f"%{name}%"))
            )

        result = await db.execute(query)
        return result.scalar() or 0

    @staticmethod
    async def get_actor_with_films(db: AsyncSession, actor_id: int) -> Optional[Actor]:
        """Get an actor with their films."""
        query = (
            select(Actor)
            .where(Actor.actor_id == actor_id)
            .options(selectinload(Actor.film_actors).selectinload("film"))
        )
        result = await db.execute(query)
        return result.scalar_one_or_none()