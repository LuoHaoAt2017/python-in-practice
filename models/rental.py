from sqlalchemy import Integer, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from typing import Optional

from .base import Base, TimestampMixin


class Rental(Base, TimestampMixin):
    """Rental model representing film rentals."""
    __tablename__ = "rental"

    rental_id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    rental_date: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    inventory_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("inventory.inventory_id"), nullable=False
    )
    customer_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("customer.customer_id"), nullable=False
    )
    return_date: Mapped[Optional[datetime]] = mapped_column(DateTime)
    staff_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("staff.staff_id"), nullable=False
    )

    # Relationships
    inventory: Mapped["Inventory"] = relationship("Inventory", back_populates="rentals")
    customer: Mapped["Customer"] = relationship("Customer", back_populates="rentals")
    staff: Mapped["Staff"] = relationship("Staff", back_populates="rentals")
    payment: Mapped[Optional["Payment"]] = relationship(
        "Payment", back_populates="rental", uselist=False
    )

    def __repr__(self):
        return f"<Rental(rental_id={self.rental_id}, rental_date={self.rental_date})>"