from sqlalchemy import Integer, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from typing import List, Optional

from .base import Base, TimestampMixin


class Inventory(Base, TimestampMixin):
    """Inventory model representing film copies in stores."""
    __tablename__ = "inventory"

    inventory_id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    film_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("film.film_id"), nullable=False
    )
    store_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("store.store_id"), nullable=False
    )

    # Relationships
    film: Mapped["Film"] = relationship("Film", back_populates="inventories")
    store: Mapped["Store"] = relationship("Store", back_populates="inventories")
    rentals: Mapped[List["Rental"]] = relationship(
        "Rental", back_populates="inventory", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Inventory(inventory_id={self.inventory_id}, film_id={self.film_id}, store_id={self.store_id})>"