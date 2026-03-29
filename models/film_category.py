from sqlalchemy import Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class FilmCategory(Base):
    """Many-to-many relationship between films and categories."""
    __tablename__ = "film_category"

    film_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("film.film_id"), primary_key=True
    )
    category_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("category.category_id"), primary_key=True
    )

    # Relationships
    film: Mapped["Film"] = relationship("Film", back_populates="film_categories")
    category: Mapped["Category"] = relationship("Category", back_populates="film_categories")

    def __repr__(self):
        return f"<FilmCategory(film_id={self.film_id}, category_id={self.category_id})>"