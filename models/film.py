from sqlalchemy import Integer, String, Text, Numeric, DateTime, ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from typing import List, Optional

from .base import Base, TimestampMixin


class Film(Base, TimestampMixin):
    """Film model representing films available for rental."""
    __tablename__ = "film"

    film_id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text)
    release_year: Mapped[Optional[int]] = mapped_column(Integer)
    language_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("language.language_id"), nullable=False
    )
    original_language_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("language.language_id")
    )
    rental_duration: Mapped[int] = mapped_column(Integer, nullable=False, default=3)
    rental_rate: Mapped[float] = mapped_column(Numeric(4, 2), nullable=False, default=4.99)
    length: Mapped[Optional[int]] = mapped_column(Integer)
    replacement_cost: Mapped[float] = mapped_column(
        Numeric(5, 2), nullable=False, default=19.99
    )
    rating: Mapped[Optional[str]] = mapped_column(String(5), default="G")
    special_features: Mapped[Optional[str]] = mapped_column(String(100))

    # Relationships
    language: Mapped["Language"] = relationship(
        "Language", foreign_keys=[language_id], back_populates="films"
    )
    original_language: Mapped[Optional["Language"]] = relationship(
        "Language", foreign_keys=[original_language_id]
    )
    film_actors: Mapped[List["FilmActor"]] = relationship(
        "FilmActor", back_populates="film", cascade="all, delete-orphan"
    )
    film_categories: Mapped[List["FilmCategory"]] = relationship(
        "FilmCategory", back_populates="film", cascade="all, delete-orphan"
    )
    inventories: Mapped[List["Inventory"]] = relationship(
        "Inventory", back_populates="film", cascade="all, delete-orphan"
    )

    # Indexes
    __table_args__ = (
        Index("idx_film_title", "title"),
        Index("idx_fk_language_id", "language_id"),
        Index("idx_fk_original_language_id", "original_language_id"),
    )

    def __repr__(self):
        return f"<Film(film_id={self.film_id}, title='{self.title}')>"