from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.stats import OverviewStats, CategoryStats, CategoryStatsResponse
from app.services.stats_service import stats_service

router = APIRouter()


@router.get("/stats/overview", response_model=OverviewStats)
async def get_overview_statistics(db: Session = Depends(get_db)):
    """
    Get overview statistics for the entire book collection

    Returns:
    - Total number of books
    - Average price across all books
    - Distribution of ratings (count per rating 1-5)
    - Total number of categories
    """
    stats = stats_service.get_overview_stats(db)

    return OverviewStats(**stats)


@router.get("/stats/categories", response_model=CategoryStatsResponse)
async def get_category_statistics(db: Session = Depends(get_db)):
    """
    Get detailed statistics for each category

    Returns statistics for each category including:
    - Number of books
    - Average price
    - Average rating

    Categories are sorted by book count (descending)
    """
    category_stats = stats_service.get_category_stats(db)

    return CategoryStatsResponse(
        categories=[CategoryStats(**stats) for stats in category_stats],
        total_categories=len(category_stats)
    )
