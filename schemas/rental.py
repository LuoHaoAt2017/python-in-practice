from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict


# Base schema with common fields
class RentalBase(BaseModel):
    inventory_id: int
    customer_id: int
    staff_id: int


# Schema for creating a rental
class RentalCreate(RentalBase):
    pass


# Schema for updating a rental (all fields optional)
class RentalUpdate(BaseModel):
    inventory_id: Optional[int] = None
    customer_id: Optional[int] = None
    staff_id: Optional[int] = None
    return_date: Optional[datetime] = None


# Schema for rental response
class RentalResponse(RentalBase):
    rental_id: int
    rental_date: datetime
    return_date: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# Schema for rental with related film
class RentalWithFilm(RentalResponse):
    film: Optional["FilmResponse"] = None  # Forward reference


# Schema for rental list response (pagination)
class RentalListResponse(BaseModel):
    items: list[RentalResponse]
    total: int
    page: int
    size: int
    pages: int