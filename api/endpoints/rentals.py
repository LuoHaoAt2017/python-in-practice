from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from config.database import get_async_db
from services.rental import RentalService
from schemas.rental import (
    RentalCreate,
    RentalUpdate,
    RentalResponse,
    RentalListResponse,
    RentalWithFilm,
)

router = APIRouter()


@router.get("/", response_model=RentalListResponse)
async def get_rentals(
    db: AsyncSession = Depends(get_async_db),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of records to return"),
    customer_id: Optional[int] = Query(None, description="Filter by customer ID"),
    inventory_id: Optional[int] = Query(None, description="Filter by inventory ID"),
    staff_id: Optional[int] = Query(None, description="Filter by staff ID"),
    returned: Optional[bool] = Query(None, description="Filter by return status"),
    start_date: Optional[datetime] = Query(None, description="Filter by start date"),
    end_date: Optional[datetime] = Query(None, description="Filter by end date"),
):
    """Get list of rentals with pagination and optional filtering."""
    rentals = await RentalService.get_rentals(
        db,
        skip=skip,
        limit=limit,
        customer_id=customer_id,
        inventory_id=inventory_id,
        staff_id=staff_id,
        returned=returned,
        start_date=start_date,
        end_date=end_date,
    )
    total = await RentalService.get_rentals_count(
        db,
        customer_id=customer_id,
        inventory_id=inventory_id,
        staff_id=staff_id,
        returned=returned,
        start_date=start_date,
        end_date=end_date,
    )

    return RentalListResponse(
        items=rentals,
        total=total,
        page=skip // limit + 1 if limit > 0 else 1,
        size=limit,
        pages=(total + limit - 1) // limit if limit > 0 else 1,
    )


@router.get("/{rental_id}", response_model=RentalResponse)
async def get_rental(
    rental_id: int,
    db: AsyncSession = Depends(get_async_db),
):
    """Get a rental by ID."""
    rental = await RentalService.get_rental_by_id(db, rental_id)
    if not rental:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Rental with ID {rental_id} not found",
        )
    return rental


@router.get("/{rental_id}/details", response_model=RentalWithFilm)
async def get_rental_with_details(
    rental_id: int,
    db: AsyncSession = Depends(get_async_db),
):
    """Get a rental with film and customer details."""
    rental = await RentalService.get_rental_with_details(db, rental_id)
    if not rental:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Rental with ID {rental_id} not found",
        )
    return rental


@router.post("/", response_model=RentalResponse, status_code=status.HTTP_201_CREATED)
async def create_rental(
    rental_data: RentalCreate,
    db: AsyncSession = Depends(get_async_db),
):
    """Create a new rental."""
    rental = await RentalService.create_rental(db, rental_data)
    return rental


@router.put("/{rental_id}", response_model=RentalResponse)
async def update_rental(
    rental_id: int,
    rental_data: RentalUpdate,
    db: AsyncSession = Depends(get_async_db),
):
    """Update a rental."""
    rental = await RentalService.update_rental(db, rental_id, rental_data)
    if not rental:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Rental with ID {rental_id} not found",
        )
    return rental


@router.put("/{rental_id}/return", response_model=RentalResponse)
async def return_rental(
    rental_id: int,
    db: AsyncSession = Depends(get_async_db),
):
    """Mark a rental as returned."""
    rental = await RentalService.return_rental(db, rental_id)
    if not rental:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Rental with ID {rental_id} not found or already returned",
        )
    return rental


@router.delete("/{rental_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_rental(
    rental_id: int,
    db: AsyncSession = Depends(get_async_db),
):
    """Delete a rental."""
    success = await RentalService.delete_rental(db, rental_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Rental with ID {rental_id} not found",
        )