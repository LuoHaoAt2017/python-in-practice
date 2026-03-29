from sqlalchemy import Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class FilmActor(Base):
    """Many-to-many relationship between films and actors."""
    __tablename__ = "film_actor"

    actor_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("actor.actor_id"), primary_key=True
    )
    film_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("film.film_id"), primary_key=True
    )

    # Relationships
    actor: Mapped["Actor"] = relationship("Actor", back_populates="film_actors")
    film: Mapped["Film"] = relationship("Film", back_populates="film_actors")

    def __repr__(self):
        return f"<FilmActor(actor_id={self.actor_id}, film_id={self.film_id})>"