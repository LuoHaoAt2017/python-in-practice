from sqlalchemy import Integer, String, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from typing import List

from .base import Base, TimestampMixin


class Language(Base, TimestampMixin):
    """Language model representing film languages."""
    __tablename__ = "language"

    language_id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(20), nullable=False)

    # Relationships
    films: Mapped[List["Film"]] = relationship(
        "Film", foreign_keys="[Film.language_id]", back_populates="language"
    )

    def __repr__(self):
        return f"<Language(language_id={self.language_id}, name='{self.name}')>"