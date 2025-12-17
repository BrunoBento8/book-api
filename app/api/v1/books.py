from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
from app.database import get_db
from app.schemas.book import BookResponse, BookListResponse
from app.services.book_service import book_service
import math

router = APIRouter()


@router.get("/books", response_model=BookListResponse)
async def get_books(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    db: Session = Depends(get_db)
):
    """
    Get paginated list of all books

    - **page**: Page number (default: 1)
    - **page_size**: Number of items per page (default: 20, max: 100)
    """
    books, total = book_service.get_books(db, page, page_size)
    total_pages = math.ceil(total / page_size)

    return BookListResponse(
        books=[BookResponse.model_validate(book) for book in books],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages
    )


@router.get("/books/search", response_model=list[BookResponse])
async def search_books(
    title: Optional[str] = Query(None, description="Search by book title (case-insensitive)"),
    category: Optional[str] = Query(None, description="Filter by category"),
    db: Session = Depends(get_db)
):
    """
    Search books by title and/or category

    - **title**: Search term for book title (partial match, case-insensitive)
    - **category**: Exact category name

    At least one parameter must be provided.
    """
    if not title and not category:
        raise HTTPException(
            status_code=400,
            detail="At least one search parameter (title or category) must be provided"
        )

    books = book_service.search_books(db, title, category)

    return [BookResponse.model_validate(book) for book in books]


@router.get("/books/top-rated", response_model=list[BookResponse])
async def get_top_rated_books(
    limit: int = Query(10, ge=1, le=100, description="Number of books to return"),
    db: Session = Depends(get_db)
):
    """
    Get top-rated books (rating >= 4)

    Books are ordered by rating (descending), then by price (ascending)

    - **limit**: Maximum number of books to return (default: 10, max: 100)
    """
    books = book_service.get_top_rated_books(db, limit)

    return [BookResponse.model_validate(book) for book in books]


@router.get("/books/price-range", response_model=list[BookResponse])
async def get_books_by_price_range(
    min: float = Query(0, ge=0, description="Minimum price"),
    max: float = Query(100, ge=0, description="Maximum price"),
    db: Session = Depends(get_db)
):
    """
    Get books within a specific price range

    - **min**: Minimum price (default: 0)
    - **max**: Maximum price (default: 100)
    """
    if min > max:
        raise HTTPException(
            status_code=400,
            detail="Minimum price cannot be greater than maximum price"
        )

    books = book_service.get_books_by_price_range(db, min, max)

    return [BookResponse.model_validate(book) for book in books]


# IMPORTANT: This must be the last route because it has a dynamic path parameter
@router.get("/books/{book_id}", response_model=BookResponse)
async def get_book(
    book_id: int,
    db: Session = Depends(get_db)
):
    """
    Get a specific book by ID

    - **book_id**: Book ID
    """
    book = book_service.get_book_by_id(db, book_id)

    if not book:
        raise HTTPException(
            status_code=404,
            detail=f"Book with ID {book_id} not found"
        )

    return BookResponse.model_validate(book)
