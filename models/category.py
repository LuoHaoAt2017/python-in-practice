from sqlalchemy import Integer, String, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from typing import List

from .base import Base, TimestampMixin


class Category(Base, TimestampMixin):
    """Category model representing film categories."""
    __tablename__ = "category"

    category_id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(25), nullable=False)

    # Relationships
    film_categories: Mapped[List["FilmCategory"]] = relationship(
        "FilmCategory", back_populates="category", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Category(category_id={self.category_id}, name='{self.name}')>"