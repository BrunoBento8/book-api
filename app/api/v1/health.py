from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.database import get_db
from app.config import settings

router = APIRouter()


@router.get("/health")
async def health_check(db: Session = Depends(get_db)):
    """
    Endpoint de verificação de saúde
    Verifica conectividade da API e banco de dados
    """
    try:
        # Testa conexão com banco de dados
        db.execute(text("SELECT 1"))
        db_status = "conectado"
    except Exception as e:
        db_status = f"erro: {str(e)}"

    return {
        "status": "saudável",
        "app_name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT,
        "database": db_status
    }
