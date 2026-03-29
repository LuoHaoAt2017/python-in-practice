from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_, and_
from sqlalchemy.orm import selectinload

from models.customer import Customer
from schemas.customer import CustomerCreate, CustomerUpdate


class CustomerService:
    """Service for customer-related operations."""

    @staticmethod
    async def get_customers(
        db: AsyncSession,
        skip: int = 0,
        limit: int = 100,
        name: Optional[str] = None,
        email: Optional[str] = None,
        active: Optional[bool] = None,
        store_id: Optional[int] = None,
    ) -> List[Customer]:
        """Get list of customers with optional filtering and pagination."""
        query = select(Customer).order_by(Customer.last_name, Customer.first_name)

        filters = []
        if name:
            filters.append(
                or_(
                    Customer.first_name.ilike(f"%{name}%"),
                    Customer.last_name.ilike(f"%{name}%"),
                )
            )
        if email:
            filters.append(Customer.email.ilike(f"%{email}%"))
        if active is not None:
            filters.append(Customer.activebool == active)
        if store_id:
            filters.append(Customer.store_id == store_id)

        if filters:
            query = query.where(and_(*filters))

        if limit > 0:
            query = query.offset(skip).limit(limit)

        result = await db.execute(query)
        return result.scalars().all()

    @staticmethod
    async def get_customer_by_id(db: AsyncSession, customer_id: int) -> Optional[Customer]:
        """Get a customer by ID."""
        query = select(Customer).where(Customer.customer_id == customer_id)
        result = await db.execute(query)
        return result.scalar_one_or_none()

    @staticmethod
    async def create_customer(db: AsyncSession, customer_data: CustomerCreate) -> Customer:
        """Create a new customer."""
        from datetime import datetime

        customer = Customer(
            store_id=customer_data.store_id,
            first_name=customer_data.first_name,
            last_name=customer_data.last_name,
            email=customer_data.email,
            address_id=customer_data.address_id,
            activebool=customer_data.activebool,
            create_date=datetime.now(),
            active=customer_data.active,
        )
        db.add(customer)
        await db.commit()
        await db.refresh(customer)
        return customer

    @staticmethod
    async def update_customer(
        db: AsyncSession,
        customer_id: int,
        customer_data: CustomerUpdate
    ) -> Optional[Customer]:
        """Update an existing customer."""
        customer = await CustomerService.get_customer_by_id(db, customer_id)
        if not customer:
            return None

        update_data = customer_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(customer, field, value)

        await db.commit()
        await db.refresh(customer)
        return customer

    @staticmethod
    async def delete_customer(db: AsyncSession, customer_id: int) -> bool:
        """Delete a customer."""
        customer = await CustomerService.get_customer_by_id(db, customer_id)
        if not customer:
            return False

        await db.delete(customer)
        await db.commit()
        return True

    @staticmethod
    async def get_customers_count(
        db: AsyncSession,
        name: Optional[str] = None,
        email: Optional[str] = None,
        active: Optional[bool] = None,
        store_id: Optional[int] = None,
    ) -> int:
        """Get total count of customers with optional filtering."""
        query = select(func.count(Customer.customer_id))

        filters = []
        if name:
            filters.append(
                or_(
                    Customer.first_name.ilike(f"%{name}%"),
                    Customer.last_name.ilike(f"%{name}%"),
                )
            )
        if email:
            filters.append(Customer.email.ilike(f"%{email}%"))
        if active is not None:
            filters.append(Customer.activebool == active)
        if store_id:
            filters.append(Customer.store_id == store_id)

        if filters:
            query = query.where(and_(*filters))

        result = await db.execute(query)
        return result.scalar() or 0

    @staticmethod
    async def get_customer_with_rentals(db: AsyncSession, customer_id: int) -> Optional[Customer]:
        """Get a customer with their rentals."""
        query = (
            select(Customer)
            .where(Customer.customer_id == customer_id)
            .options(
                selectinload(Customer.rentals).selectinload("inventory").selectinload("film"),
                selectinload(Customer.payments),
            )
        )
        result = await db.execute(query)
        return result.scalar_one_or_none()