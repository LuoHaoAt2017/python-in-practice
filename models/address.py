from sqlalchemy import Integer, String, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import List, Optional

from .base import Base, TimestampMixin


class Address(Base, TimestampMixin):
    """Address model representing customer and staff addresses."""
    __tablename__ = "address"

    address_id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    address: Mapped[str] = mapped_column(String(50), nullable=False)
    address2: Mapped[Optional[str]] = mapped_column(String(50))
    district: Mapped[str] = mapped_column(String(20), nullable=False)
    city_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("city.city_id"), nullable=False
    )
    postal_code: Mapped[Optional[str]] = mapped_column(String(10))
    phone: Mapped[str] = mapped_column(String(20), nullable=False)

    # Relationships
    city: Mapped["City"] = relationship("City", back_populates="addresses")
    customers: Mapped[List["Customer"]] = relationship(
        "Customer", back_populates="address", cascade="all, delete-orphan"
    )
    staff: Mapped[List["Staff"]] = relationship(
        "Staff", back_populates="address", cascade="all, delete-orphan"
    )
    stores: Mapped[List["Store"]] = relationship(
        "Store", back_populates="address", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Address(address_id={self.address_id}, address='{self.address[:20]}...')>"