from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.book import CategoryResponse
from app.services.book_service import book_service

router = APIRouter()


@router.get("/categories", response_model=list[CategoryResponse])
async def get_categories(db: Session = Depends(get_db)):
    """
    Get all unique book categories with counts

    Returns a list of categories sorted by book count (descending)
    """
    categories = book_service.get_categories(db)

    return [
        CategoryResponse(category=category, count=count)
        for category, count in categories
    ]
