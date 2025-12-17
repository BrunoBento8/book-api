from pydantic import BaseModel
from typing import Dict


class OverviewStats(BaseModel):
    """Overview statistics for the book collection"""
    total_books: int
    average_price: float
    rating_distribution: Dict[int, int]  # {rating: count}
    total_categories: int


class CategoryStats(BaseModel):
    """Statistics for a single category"""
    category: str
    book_count: int
    average_price: float
    average_rating: float


class CategoryStatsResponse(BaseModel):
    """Response for category statistics"""
    categories: list[CategoryStats]
    total_categories: int
