from sqlalchemy import Integer, String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import List

from .base import Base, TimestampMixin


class City(Base, TimestampMixin):
    """City model representing cities."""
    __tablename__ = "city"

    city_id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    city: Mapped[str] = mapped_column(String(50), nullable=False)
    country_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("country.country_id"), nullable=False
    )

    # Relationships
    country: Mapped["Country"] = relationship("Country", back_populates="cities")
    addresses: Mapped[List["Address"]] = relationship(
        "Address", back_populates="city", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<City(city_id={self.city_id}, city='{self.city}')>"