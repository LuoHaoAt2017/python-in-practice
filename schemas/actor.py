from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict


# Base schema with common fields
class ActorBase(BaseModel):
    first_name: str
    last_name: str


# Schema for creating an actor
class ActorCreate(ActorBase):
    pass


# Schema for updating an actor (all fields optional)
class ActorUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None


# Schema for actor response
class ActorResponse(ActorBase):
    actor_id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# Schema for actor with related films
class ActorWithFilms(ActorResponse):
    films: list["FilmResponse"] = []  # Forward reference


# Schema for actor list response (pagination)
class ActorListResponse(BaseModel):
    items: list[ActorResponse]
    total: int
    page: int
    size: int
    pages: int