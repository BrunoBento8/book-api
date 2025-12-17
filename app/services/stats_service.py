from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Dict, List
from app.models.book import Book
from functools import lru_cache
from datetime import datetime, timedelta


class StatsService:
    """Service class for statistics and analytics"""

    # Cache timestamp for invalidation
    _cache_timestamp = datetime.utcnow()

    @classmethod
    def invalidate_cache(cls):
        """Invalidate statistics cache"""
        cls._cache_timestamp = datetime.utcnow()

    @staticmethod
    def get_overview_stats(db: Session) -> Dict:
        """
        Get overview statistics for the book collection
        Includes: total books, average price, rating distribution
        """
        # Total books
        total_books = db.query(Book).count()

        # Average price
        avg_price_result = db.query(func.avg(Book.price)).scalar()
        average_price = round(float(avg_price_result), 2) if avg_price_result else 0.0

        # Rating distribution
        rating_dist = db.query(
            Book.rating,
            func.count(Book.id)
        ).group_by(Book.rating).all()

        rating_distribution = {rating: count for rating, count in rating_dist}

        # Total categories
        total_categories = db.query(Book.category).distinct().count()

        return {
            "total_books": total_books,
            "average_price": average_price,
            "rating_distribution": rating_distribution,
            "total_categories": total_categories
        }

    @staticmethod
    def get_category_stats(db: Session) -> List[Dict]:
        """
        Get detailed statistics for each category
        Returns: List of category statistics
        """
        results = db.query(
            Book.category,
            func.count(Book.id).label('book_count'),
            func.avg(Book.price).label('avg_price'),
            func.avg(Book.rating).label('avg_rating')
        ).group_by(Book.category).order_by(func.count(Book.id).desc()).all()

        return [
            {
                "category": category,
                "book_count": book_count,
                "average_price": round(float(avg_price), 2) if avg_price else 0.0,
                "average_rating": round(float(avg_rating), 2) if avg_rating else 0.0
            }
            for category, book_count, avg_price, avg_rating in results
        ]


# Create singleton instance
stats_service = StatsService()
