from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from config.database import get_async_db
from services.film import FilmService
from schemas.film import (
    FilmCreate,
    FilmUpdate,
    FilmResponse,
    FilmListResponse,
    FilmWithActors,
    FilmWithCategories,
)

router = APIRouter()


@router.get("/", response_model=FilmListResponse)
async def get_films(
    db: AsyncSession = Depends(get_async_db),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of records to return"),
    title: Optional[str] = Query(None, description="Filter by film title"),
    release_year: Optional[int] = Query(None, description="Filter by release year"),
    rating: Optional[str] = Query(None, description="Filter by rating (G, PG, PG-13, R, NC-17)"),
    language_id: Optional[int] = Query(None, description="Filter by language ID"),
):
    """Get list of films with pagination and optional filtering."""
    films = await FilmService.get_films(
        db,
        skip=skip,
        limit=limit,
        title=title,
        release_year=release_year,
        rating=rating,
        language_id=language_id,
    )
    total = await FilmService.get_films_count(
        db,
        title=title,
        release_year=release_year,
        rating=rating,
        language_id=language_id,
    )

    return FilmListResponse(
        items=films,
        total=total,
        page=skip // limit + 1 if limit > 0 else 1,
        size=limit,
        pages=(total + limit - 1) // limit if limit > 0 else 1,
    )


@router.get("/{film_id}", response_model=FilmResponse)
async def get_film(
    film_id: int,
    db: AsyncSession = Depends(get_async_db),
):
    """Get a film by ID."""
    film = await FilmService.get_film_by_id(db, film_id)
    if not film:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Film with ID {film_id} not found",
        )
    return film


@router.get("/{film_id}/actors", response_model=FilmWithActors)
async def get_film_with_actors(
    film_id: int,
    db: AsyncSession = Depends(get_async_db),
):
    """Get a film with its actors."""
    film = await FilmService.get_film_with_actors(db, film_id)
    if not film:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Film with ID {film_id} not found",
        )
    return film


@router.get("/{film_id}/categories", response_model=FilmWithCategories)
async def get_film_with_categories(
    film_id: int,
    db: AsyncSession = Depends(get_async_db),
):
    """Get a film with its categories."""
    film = await FilmService.get_film_with_categories(db, film_id)
    if not film:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Film with ID {film_id} not found",
        )
    return film


@router.post("/", response_model=FilmResponse, status_code=status.HTTP_201_CREATED)
async def create_film(
    film_data: FilmCreate,
    db: AsyncSession = Depends(get_async_db),
):
    """Create a new film."""
    film = await FilmService.create_film(db, film_data)
    return film


@router.put("/{film_id}", response_model=FilmResponse)
async def update_film(
    film_id: int,
    film_data: FilmUpdate,
    db: AsyncSession = Depends(get_async_db),
):
    """Update a film."""
    film = await FilmService.update_film(db, film_id, film_data)
    if not film:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Film with ID {film_id} not found",
        )
    return film


@router.delete("/{film_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_film(
    film_id: int,
    db: AsyncSession = Depends(get_async_db),
):
    """Delete a film."""
    success = await FilmService.delete_film(db, film_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Film with ID {film_id} not found",
        )