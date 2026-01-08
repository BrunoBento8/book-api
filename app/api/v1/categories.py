from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.book import CategoryResponse
from app.services.book_service import book_service

router = APIRouter()


@router.get("/categories", response_model=list[CategoryResponse])
async def get_categories(db: Session = Depends(get_db)):
    """
    Obtém todas as categorias únicas de livros com contagens

    Retorna uma lista de categorias ordenadas por contagem de livros (decrescente)
    """
    categories = book_service.get_categories(db)

    return [
        CategoryResponse(category=category, count=count)
        for category, count in categories
    ]
