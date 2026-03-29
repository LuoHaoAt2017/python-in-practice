from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import List

from .base import Base, TimestampMixin


class Country(Base, TimestampMixin):
    """Country model representing countries."""
    __tablename__ = "country"

    country_id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    country: Mapped[str] = mapped_column(String(50), nullable=False)

    # Relationships
    cities: Mapped[List["City"]] = relationship(
        "City", back_populates="country", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Country(country_id={self.country_id}, country='{self.country}')>"