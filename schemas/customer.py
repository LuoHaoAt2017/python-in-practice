from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, EmailStr


# Base schema with common fields
class CustomerBase(BaseModel):
    store_id: int
    first_name: str
    last_name: str
    email: Optional[EmailStr] = None
    address_id: int
    activebool: bool = True
    active: Optional[int] = None


# Schema for creating a customer
class CustomerCreate(CustomerBase):
    pass


# Schema for updating a customer (all fields optional)
class CustomerUpdate(BaseModel):
    store_id: Optional[int] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[EmailStr] = None
    address_id: Optional[int] = None
    activebool: Optional[bool] = None
    active: Optional[int] = None


# Schema for customer response
class CustomerResponse(CustomerBase):
    customer_id: int
    create_date: datetime
    last_update: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


# Schema for customer with related rentals
class CustomerWithRentals(CustomerResponse):
    rentals: list["RentalResponse"] = []  # Forward reference
    payments: list = []


# Schema for customer list response (pagination)
class CustomerListResponse(BaseModel):
    items: list[CustomerResponse]
    total: int
    page: int
    size: int
    pages: int