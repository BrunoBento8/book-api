from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.stats import OverviewStats, CategoryStats, CategoryStatsResponse
from app.services.stats_service import stats_service

router = APIRouter()


@router.get("/stats/overview", response_model=OverviewStats)
async def get_overview_statistics(db: Session = Depends(get_db)):
    """
    Obtém estatísticas gerais para toda a coleção de livros

    Retorna:
    - Número total de livros
    - Preço médio de todos os livros
    - Distribuição de avaliações (contagem por avaliação 1-5)
    - Número total de categorias
    """
    stats = stats_service.get_overview_stats(db)

    return OverviewStats(**stats)


@router.get("/stats/categories", response_model=CategoryStatsResponse)
async def get_category_statistics(db: Session = Depends(get_db)):
    """
    Obtém estatísticas detalhadas para cada categoria

    Retorna estatísticas para cada categoria incluindo:
    - Número de livros
    - Preço médio
    - Avaliação média

    Categorias são ordenadas por contagem de livros (decrescente)
    """
    category_stats = stats_service.get_category_stats(db)

    return CategoryStatsResponse(
        categories=[CategoryStats(**stats) for stats in category_stats],
        total_categories=len(category_stats)
    )
