from sqlalchemy import Integer, String, Boolean, LargeBinary, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import List, Optional

from .base import Base, TimestampMixin


class Staff(Base, TimestampMixin):
    """Staff model representing store staff."""
    __tablename__ = "staff"

    staff_id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    first_name: Mapped[str] = mapped_column(String(45), nullable=False)
    last_name: Mapped[str] = mapped_column(String(45), nullable=False)
    address_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("address.address_id"), nullable=False
    )
    email: Mapped[Optional[str]] = mapped_column(String(50))
    store_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("store.store_id"), nullable=False
    )
    active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    username: Mapped[str] = mapped_column(String(16), nullable=False)
    password: Mapped[Optional[str]] = mapped_column(String(40))
    picture: Mapped[Optional[bytes]] = mapped_column(LargeBinary)

    # Relationships
    address: Mapped["Address"] = relationship("Address", back_populates="staff")
    store: Mapped["Store"] = relationship(
        "Store", foreign_keys=[store_id], back_populates="staff"
    )
    managed_store: Mapped[Optional["Store"]] = relationship(
        "Store", foreign_keys="[Store.manager_staff_id]", back_populates="manager"
    )
    payments: Mapped[List["Payment"]] = relationship(
        "Payment", back_populates="staff", cascade="all, delete-orphan"
    )
    rentals: Mapped[List["Rental"]] = relationship(
        "Rental", back_populates="staff", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Staff(staff_id={self.staff_id}, name='{self.first_name} {self.last_name}')>"