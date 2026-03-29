from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict


# Base schema with common fields
class FilmBase(BaseModel):
    title: str
    description: Optional[str] = None
    release_year: Optional[int] = None
    language_id: int
    original_language_id: Optional[int] = None
    rental_duration: int = 3
    rental_rate: float = 4.99
    length: Optional[int] = None
    replacement_cost: float = 19.99
    rating: Optional[str] = "G"
    special_features: Optional[str] = None


# Schema for creating a film
class FilmCreate(FilmBase):
    pass


# Schema for updating a film (all fields optional)
class FilmUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    release_year: Optional[int] = None
    language_id: Optional[int] = None
    original_language_id: Optional[int] = None
    rental_duration: Optional[int] = None
    rental_rate: Optional[float] = None
    length: Optional[int] = None
    replacement_cost: Optional[float] = None
    rating: Optional[str] = None
    special_features: Optional[str] = None


# Schema for film response
class FilmResponse(FilmBase):
    film_id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# Schema for film with related actors
class FilmWithActors(FilmResponse):
    actors: list["ActorResponse"] = []  # Forward reference


# Schema for film with related categories
class FilmWithCategories(FilmResponse):
    categories: list["CategoryResponse"] = []  # Forward reference


# Schema for film list response (pagination)
class FilmListResponse(BaseModel):
    items: list[FilmResponse]
    total: int
    page: int
    size: int
    pages: int