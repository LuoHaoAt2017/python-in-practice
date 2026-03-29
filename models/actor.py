from sqlalchemy import Integer, String, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from typing import List, Optional

from .base import Base, TimestampMixin


class Actor(Base, TimestampMixin):
    """Actor model representing actors in films."""
    __tablename__ = "actor"

    actor_id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    first_name: Mapped[str] = mapped_column(String(45), nullable=False)
    last_name: Mapped[str] = mapped_column(String(45), nullable=False)

    # Relationships
    film_actors: Mapped[List["FilmActor"]] = relationship(
        "FilmActor", back_populates="actor", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Actor(actor_id={self.actor_id}, name='{self.first_name} {self.last_name}')>"