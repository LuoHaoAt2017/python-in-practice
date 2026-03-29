from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from config.database import get_async_db
from services.actor import ActorService
from schemas.actor import (
    ActorCreate,
    ActorUpdate,
    ActorResponse,
    ActorListResponse,
    ActorWithFilms,
)

router = APIRouter()


@router.get("/", response_model=ActorListResponse)
async def get_actors(
    db: AsyncSession = Depends(get_async_db),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of records to return"),
    name: Optional[str] = Query(None, description="Filter by actor name (first or last)"),
):
    """Get list of actors with pagination and optional filtering."""
    actors = await ActorService.get_actors(db, skip=skip, limit=limit, name=name)
    total = await ActorService.get_actors_count(db, name=name)

    return ActorListResponse(
        items=actors,
        total=total,
        page=skip // limit + 1 if limit > 0 else 1,
        size=limit,
        pages=(total + limit - 1) // limit if limit > 0 else 1,
    )


@router.get("/{actor_id}", response_model=ActorResponse)
async def get_actor(
    actor_id: int,
    db: AsyncSession = Depends(get_async_db),
):
    """Get an actor by ID."""
    actor = await ActorService.get_actor_by_id(db, actor_id)
    if not actor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Actor with ID {actor_id} not found",
        )
    return actor


@router.get("/{actor_id}/films", response_model=ActorWithFilms)
async def get_actor_with_films(
    actor_id: int,
    db: AsyncSession = Depends(get_async_db),
):
    """Get an actor with their films."""
    actor = await ActorService.get_actor_with_films(db, actor_id)
    if not actor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Actor with ID {actor_id} not found",
        )
    return actor


@router.post("/", response_model=ActorResponse, status_code=status.HTTP_201_CREATED)
async def create_actor(
    actor_data: ActorCreate,
    db: AsyncSession = Depends(get_async_db),
):
    """Create a new actor."""
    actor = await ActorService.create_actor(db, actor_data)
    return actor


@router.put("/{actor_id}", response_model=ActorResponse)
async def update_actor(
    actor_id: int,
    actor_data: ActorUpdate,
    db: AsyncSession = Depends(get_async_db),
):
    """Update an actor."""
    actor = await ActorService.update_actor(db, actor_id, actor_data)
    if not actor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Actor with ID {actor_id} not found",
        )
    return actor


@router.delete("/{actor_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_actor(
    actor_id: int,
    db: AsyncSession = Depends(get_async_db),
):
    """Delete an actor."""
    success = await ActorService.delete_actor(db, actor_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Actor with ID {actor_id} not found",
        )