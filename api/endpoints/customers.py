from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from config.database import get_async_db
from services.customer import CustomerService
from schemas.customer import (
    CustomerCreate,
    CustomerUpdate,
    CustomerResponse,
    CustomerListResponse,
    CustomerWithRentals,
)

router = APIRouter()


@router.get("/", response_model=CustomerListResponse)
async def get_customers(
    db: AsyncSession = Depends(get_async_db),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of records to return"),
    name: Optional[str] = Query(None, description="Filter by customer name (first or last)"),
    email: Optional[str] = Query(None, description="Filter by email"),
    active: Optional[bool] = Query(None, description="Filter by active status"),
    store_id: Optional[int] = Query(None, description="Filter by store ID"),
):
    """Get list of customers with pagination and optional filtering."""
    customers = await CustomerService.get_customers(
        db,
        skip=skip,
        limit=limit,
        name=name,
        email=email,
        active=active,
        store_id=store_id,
    )
    total = await CustomerService.get_customers_count(
        db,
        name=name,
        email=email,
        active=active,
        store_id=store_id,
    )

    return CustomerListResponse(
        items=customers,
        total=total,
        page=skip // limit + 1 if limit > 0 else 1,
        size=limit,
        pages=(total + limit - 1) // limit if limit > 0 else 1,
    )


@router.get("/{customer_id}", response_model=CustomerResponse)
async def get_customer(
    customer_id: int,
    db: AsyncSession = Depends(get_async_db),
):
    """Get a customer by ID."""
    customer = await CustomerService.get_customer_by_id(db, customer_id)
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Customer with ID {customer_id} not found",
        )
    return customer


@router.get("/{customer_id}/rentals", response_model=CustomerWithRentals)
async def get_customer_with_rentals(
    customer_id: int,
    db: AsyncSession = Depends(get_async_db),
):
    """Get a customer with their rentals and payments."""
    customer = await CustomerService.get_customer_with_rentals(db, customer_id)
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Customer with ID {customer_id} not found",
        )
    return customer


@router.post("/", response_model=CustomerResponse, status_code=status.HTTP_201_CREATED)
async def create_customer(
    customer_data: CustomerCreate,
    db: AsyncSession = Depends(get_async_db),
):
    """Create a new customer."""
    customer = await CustomerService.create_customer(db, customer_data)
    return customer


@router.put("/{customer_id}", response_model=CustomerResponse)
async def update_customer(
    customer_id: int,
    customer_data: CustomerUpdate,
    db: AsyncSession = Depends(get_async_db),
):
    """Update a customer."""
    customer = await CustomerService.update_customer(db, customer_id, customer_data)
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Customer with ID {customer_id} not found",
        )
    return customer


@router.delete("/{customer_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_customer(
    customer_id: int,
    db: AsyncSession = Depends(get_async_db),
):
    """Delete a customer."""
    success = await CustomerService.delete_customer(db, customer_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Customer with ID {customer_id} not found",
        )