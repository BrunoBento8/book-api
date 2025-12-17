from pydantic import BaseModel, Field
from typing import Optional


class BookBase(BaseModel):
    """Base book schema"""
    title: str = Field(..., min_length=1, max_length=500)
    price: float = Field(..., ge=0)
    rating: int = Field(..., ge=1, le=5)
    availability: int = Field(..., ge=0)
    category: str = Field(..., min_length=1, max_length=100)
    image_url: Optional[str] = None


class BookCreate(BookBase):
    """Schema for creating a book"""
    pass


class BookResponse(BookBase):
    """Schema for book response"""
    id: int

    class Config:
        from_attributes = True  # For Pydantic v2 (was orm_mode in v1)


class BookListResponse(BaseModel):
    """Schema for paginated book list"""
    books: list[BookResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class CategoryResponse(BaseModel):
    """Schema for category with count"""
    category: str
    count: int
