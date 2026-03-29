from sqlalchemy import Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import List, Optional

from .base import Base, TimestampMixin


class Store(Base, TimestampMixin):
    """Store model representing rental stores."""
    __tablename__ = "store"

    store_id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    manager_staff_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("staff.staff_id"), nullable=False, unique=True
    )
    address_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("address.address_id"), nullable=False
    )

    # Relationships
    manager: Mapped["Staff"] = relationship(
        "Staff", foreign_keys=[manager_staff_id], back_populates="managed_store"
    )
    address: Mapped["Address"] = relationship("Address", back_populates="stores")
    customers: Mapped[List["Customer"]] = relationship(
        "Customer", back_populates="store", cascade="all, delete-orphan"
    )
    inventories: Mapped[List["Inventory"]] = relationship(
        "Inventory", back_populates="store", cascade="all, delete-orphan"
    )
    staff: Mapped[List["Staff"]] = relationship(
        "Staff", foreign_keys="[Staff.store_id]", back_populates="store"
    )

    def __repr__(self):
        return f"<Store(store_id={self.store_id})>"