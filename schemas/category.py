from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict


# Base schema with common fields
class CategoryBase(BaseModel):
    name: str


# Schema for creating a category
class CategoryCreate(CategoryBase):
    pass


# Schema for updating a category (all fields optional)
class CategoryUpdate(BaseModel):
    name: Optional[str] = None


# Schema for category response
class CategoryResponse(CategoryBase):
    category_id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# Schema for category list response (pagination)
class CategoryListResponse(BaseModel):
    items: list[CategoryResponse]
    total: int
    page: int
    size: int
    pages: int