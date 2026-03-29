from sqlalchemy import Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from typing import List, Optional

from .base import Base, TimestampMixin


class Customer(Base, TimestampMixin):
    """Customer model representing store customers."""
    __tablename__ = "customer"

    customer_id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    store_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("store.store_id"), nullable=False
    )
    first_name: Mapped[str] = mapped_column(String(45), nullable=False)
    last_name: Mapped[str] = mapped_column(String(45), nullable=False)
    email: Mapped[Optional[str]] = mapped_column(String(50))
    address_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("address.address_id"), nullable=False
    )
    activebool: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    create_date: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    last_update: Mapped[Optional[datetime]] = mapped_column(DateTime)
    active: Mapped[Optional[int]] = mapped_column(Integer)

    # Relationships
    store: Mapped["Store"] = relationship("Store", back_populates="customers")
    address: Mapped["Address"] = relationship("Address", back_populates="customers")
    payments: Mapped[List["Payment"]] = relationship(
        "Payment", back_populates="customer", cascade="all, delete-orphan"
    )
    rentals: Mapped[List["Rental"]] = relationship(
        "Rental", back_populates="customer", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Customer(customer_id={self.customer_id}, name='{self.first_name} {self.last_name}')>"