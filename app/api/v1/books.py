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
    page: int = Query(1, ge=1, description="Número da página"),
    page_size: int = Query(20, ge=1, le=100, description="Itens por página"),
    db: Session = Depends(get_db)
):
    """
    Obtém lista paginada de todos os livros

    - **page**: Número da página (padrão: 1)
    - **page_size**: Número de itens por página (padrão: 20, máx: 100)
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
    title: Optional[str] = Query(None, description="Buscar por título do livro (não diferencia maiúsculas/minúsculas)"),
    category: Optional[str] = Query(None, description="Filtrar por categoria"),
    db: Session = Depends(get_db)
):
    """
    Busca livros por título e/ou categoria

    - **title**: Termo de busca para título do livro (correspondência parcial, não diferencia maiúsculas)
    - **category**: Nome exato da categoria

    Pelo menos um parâmetro deve ser fornecido.
    """
    if not title and not category:
        raise HTTPException(
            status_code=400,
            detail="Pelo menos um parâmetro de busca (título ou categoria) deve ser fornecido"
        )

    books = book_service.search_books(db, title, category)

    return [BookResponse.model_validate(book) for book in books]


@router.get("/books/top-rated", response_model=list[BookResponse])
async def get_top_rated_books(
    limit: int = Query(10, ge=1, le=100, description="Número de livros a retornar"),
    db: Session = Depends(get_db)
):
    """
    Obtém livros mais bem avaliados (avaliação >= 4)

    Livros são ordenados por avaliação (decrescente), depois por preço (crescente)

    - **limit**: Número máximo de livros a retornar (padrão: 10, máx: 100)
    """
    books = book_service.get_top_rated_books(db, limit)

    return [BookResponse.model_validate(book) for book in books]


@router.get("/books/price-range", response_model=list[BookResponse])
async def get_books_by_price_range(
    min: float = Query(0, ge=0, description="Preço mínimo"),
    max: float = Query(100, ge=0, description="Preço máximo"),
    db: Session = Depends(get_db)
):
    """
    Obtém livros dentro de uma faixa de preço específica

    - **min**: Preço mínimo (padrão: 0)
    - **max**: Preço máximo (padrão: 100)
    """
    if min > max:
        raise HTTPException(
            status_code=400,
            detail="O preço mínimo não pode ser maior que o preço máximo"
        )

    books = book_service.get_books_by_price_range(db, min, max)

    return [BookResponse.model_validate(book) for book in books]


# IMPORTANTE: Esta deve ser a última rota porque possui um parâmetro de caminho dinâmico
@router.get("/books/{book_id}", response_model=BookResponse)
async def get_book(
    book_id: int,
    db: Session = Depends(get_db)
):
    """
    Obtém um livro específico por ID

    - **book_id**: ID do livro
    """
    book = book_service.get_book_by_id(db, book_id)

    if not book:
        raise HTTPException(
            status_code=404,
            detail=f"Livro com ID {book_id} não encontrado"
        )

    return BookResponse.model_validate(book)
