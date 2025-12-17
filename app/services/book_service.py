from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Tuple, Optional
from app.models.book import Book


class BookService:
    """Service class for book-related business logic"""

    @staticmethod
    def get_books(db: Session, page: int = 1, page_size: int = 20) -> Tuple[List[Book], int]:
        """
        Get paginated list of books
        Returns: (books, total_count)
        """
        offset = (page - 1) * page_size
        total = db.query(Book).count()
        books = db.query(Book).offset(offset).limit(page_size).all()
        return books, total

    @staticmethod
    def get_book_by_id(db: Session, book_id: int) -> Optional[Book]:
        """Get a book by its ID"""
        return db.query(Book).filter(Book.id == book_id).first()

    @staticmethod
    def search_books(
        db: Session,
        title: Optional[str] = None,
        category: Optional[str] = None
    ) -> List[Book]:
        """
        Search books by title and/or category
        Uses case-insensitive search for title
        """
        query = db.query(Book)

        if title:
            query = query.filter(Book.title.ilike(f"%{title}%"))

        if category:
            query = query.filter(Book.category == category)

        return query.all()

    @staticmethod
    def get_categories(db: Session) -> List[Tuple[str, int]]:
        """
        Get all unique categories with book counts
        Returns: List of (category, count) tuples
        """
        return (
            db.query(Book.category, func.count(Book.id))
            .group_by(Book.category)
            .order_by(func.count(Book.id).desc())
            .all()
        )

    @staticmethod
    def get_top_rated_books(db: Session, limit: int = 10) -> List[Book]:
        """
        Get top rated books (rating >= 4)
        Ordered by rating DESC, then by price ASC
        """
        return (
            db.query(Book)
            .filter(Book.rating >= 4)
            .order_by(Book.rating.desc(), Book.price.asc())
            .limit(limit)
            .all()
        )

    @staticmethod
    def get_books_by_price_range(
        db: Session,
        min_price: float = 0,
        max_price: float = 100
    ) -> List[Book]:
        """Get books within a specific price range"""
        return (
            db.query(Book)
            .filter(Book.price >= min_price, Book.price <= max_price)
            .order_by(Book.price.asc())
            .all()
        )


# Create singleton instance
book_service = BookService()
