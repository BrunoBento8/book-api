from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.api.v1 import health, books, categories, stats, auth, scraping, ml
from app.utils.middleware import LoggingMiddleware

# Cria aplicação FastAPI
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="API de Recomendação de Livros - Tech Challenge Fase 1",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configura CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS if settings.ALLOWED_ORIGINS != ["*"] else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Adiciona middleware de logging
app.add_middleware(LoggingMiddleware)

# Inclui routers
app.include_router(health.router, prefix="/api/v1", tags=["Saúde"])
app.include_router(books.router, prefix="/api/v1", tags=["Livros"])
app.include_router(categories.router, prefix="/api/v1", tags=["Categorias"])
app.include_router(stats.router, prefix="/api/v1", tags=["Estatísticas"])
app.include_router(auth.router, prefix="/api/v1", tags=["Autenticação"])
app.include_router(scraping.router, prefix="/api/v1", tags=["Admin"])
app.include_router(ml.router, prefix="/api/v1", tags=["Pipeline ML"])


@app.get("/")
async def root():
    """Endpoint raiz com informações da API"""
    return {
        "message": "Bem-vindo à API de Recomendação de Livros",
        "version": settings.APP_VERSION,
        "docs": "/docs",
        "health": "/api/v1/health"
    }


@app.on_event("startup")
async def startup_event():
    """Executado ao iniciar a aplicação"""
    print(f"🚀 Iniciando {settings.APP_NAME} v{settings.APP_VERSION}")
    print(f"📝 Ambiente: {settings.ENVIRONMENT}")
    print(f"📚 Documentação da API disponível em: /docs")


@app.on_event("shutdown")
async def shutdown_event():
    """Executado ao encerrar a aplicação"""
    print(f"👋 Encerrando {settings.APP_NAME}")
