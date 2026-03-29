from typing import List, Optional
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_, desc
from sqlalchemy.orm import selectinload

from models.rental import Rental
from schemas.rental import RentalCreate, RentalUpdate


class RentalService:
    """Service for rental-related operations."""

    @staticmethod
    async def get_rentals(
        db: AsyncSession,
        skip: int = 0,
        limit: int = 100,
        customer_id: Optional[int] = None,
        inventory_id: Optional[int] = None,
        staff_id: Optional[int] = None,
        returned: Optional[bool] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> List[Rental]:
        """Get list of rentals with optional filtering and pagination."""
        query = select(Rental).order_by(desc(Rental.rental_date))

        filters = []
        if customer_id:
            filters.append(Rental.customer_id == customer_id)
        if inventory_id:
            filters.append(Rental.inventory_id == inventory_id)
        if staff_id:
            filters.append(Rental.staff_id == staff_id)
        if returned is not None:
            if returned:
                filters.append(Rental.return_date.is_not(None))
            else:
                filters.append(Rental.return_date.is_(None))
        if start_date:
            filters.append(Rental.rental_date >= start_date)
        if end_date:
            filters.append(Rental.rental_date <= end_date)

        if filters:
            query = query.where(and_(*filters))

        if limit > 0:
            query = query.offset(skip).limit(limit)

        result = await db.execute(query)
        return result.scalars().all()

    @staticmethod
    async def get_rental_by_id(db: AsyncSession, rental_id: int) -> Optional[Rental]:
        """Get a rental by ID."""
        query = select(Rental).where(Rental.rental_id == rental_id)
        result = await db.execute(query)
        return result.scalar_one_or_none()

    @staticmethod
    async def create_rental(db: AsyncSession, rental_data: RentalCreate) -> Rental:
        """Create a new rental."""
        rental = Rental(
            inventory_id=rental_data.inventory_id,
            customer_id=rental_data.customer_id,
            staff_id=rental_data.staff_id,
            rental_date=datetime.now(),
        )
        db.add(rental)
        await db.commit()
        await db.refresh(rental)
        return rental

    @staticmethod
    async def update_rental(
        db: AsyncSession,
        rental_id: int,
        rental_data: RentalUpdate
    ) -> Optional[Rental]:
        """Update an existing rental."""
        rental = await RentalService.get_rental_by_id(db, rental_id)
        if not rental:
            return None

        update_data = rental_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(rental, field, value)

        await db.commit()
        await db.refresh(rental)
        return rental

    @staticmethod
    async def delete_rental(db: AsyncSession, rental_id: int) -> bool:
        """Delete a rental."""
        rental = await RentalService.get_rental_by_id(db, rental_id)
        if not rental:
            return False

        await db.delete(rental)
        await db.commit()
        return True

    @staticmethod
    async def get_rentals_count(
        db: AsyncSession,
        customer_id: Optional[int] = None,
        inventory_id: Optional[int] = None,
        staff_id: Optional[int] = None,
        returned: Optional[bool] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> int:
        """Get total count of rentals with optional filtering."""
        query = select(func.count(Rental.rental_id))

        filters = []
        if customer_id:
            filters.append(Rental.customer_id == customer_id)
        if inventory_id:
            filters.append(Rental.inventory_id == inventory_id)
        if staff_id:
            filters.append(Rental.staff_id == staff_id)
        if returned is not None:
            if returned:
                filters.append(Rental.return_date.is_not(None))
            else:
                filters.append(Rental.return_date.is_(None))
        if start_date:
            filters.append(Rental.rental_date >= start_date)
        if end_date:
            filters.append(Rental.rental_date <= end_date)

        if filters:
            query = query.where(and_(*filters))

        result = await db.execute(query)
        return result.scalar() or 0

    @staticmethod
    async def get_rental_with_details(db: AsyncSession, rental_id: int) -> Optional[Rental]:
        """Get a rental with film and customer details."""
        query = (
            select(Rental)
            .where(Rental.rental_id == rental_id)
            .options(
                selectinload(Rental.inventory).selectinload("film"),
                selectinload(Rental.customer),
                selectinload(Rental.staff),
                selectinload(Rental.payment),
            )
        )
        result = await db.execute(query)
        return result.scalar_one_or_none()

    @staticmethod
    async def return_rental(db: AsyncSession, rental_id: int) -> Optional[Rental]:
        """Mark a rental as returned (set return_date to current time)."""
        rental = await RentalService.get_rental_by_id(db, rental_id)
        if not rental or rental.return_date is not None:
            return None

        rental.return_date = datetime.now()
        await db.commit()
        await db.refresh(rental)
        return rental