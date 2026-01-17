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

    # Inicializa banco de dados se necessário
    try:
        from app.database import engine, Base
        from sqlalchemy import inspect

        inspector = inspect(engine)
        tables = inspector.get_table_names()

        if not tables or 'books' not in tables or 'users' not in tables:
            print("⚠️  Tabelas do banco não encontradas, inicializando...")

            # Cria todas as tabelas
            Base.metadata.create_all(bind=engine)
            print("✅ Tabelas criadas com sucesso")

            # Tenta criar admin user se não existir
            try:
                from app.database import SessionLocal
                from app.models.user import User
                from app.utils.security import get_password_hash

                db = SessionLocal()
                try:
                    admin_exists = db.query(User).filter(User.username == settings.ADMIN_USERNAME).first()

                    if not admin_exists and settings.ADMIN_PASSWORD:
                        admin = User(
                            username=settings.ADMIN_USERNAME,
                            email=settings.ADMIN_EMAIL,
                            hashed_password=get_password_hash(settings.ADMIN_PASSWORD[:72]),
                            is_admin=True,
                            is_active=True
                        )
                        db.add(admin)
                        db.commit()
                        print(f"✅ Admin user criado: {settings.ADMIN_USERNAME}")
                    elif admin_exists:
                        print(f"✅ Admin user já existe: {settings.ADMIN_USERNAME}")
                    else:
                        print("⚠️  ADMIN_PASSWORD não configurado, admin não foi criado")
                finally:
                    db.close()
            except Exception as e:
                print(f"⚠️  Erro ao criar admin: {e}")
        else:
            print(f"✅ Banco de dados OK - Tabelas: {', '.join(tables)}")

    except Exception as e:
        print(f"⚠️  Erro ao verificar banco de dados: {e}")
        print("   A API pode não funcionar corretamente sem as tabelas")


@app.on_event("shutdown")
async def shutdown_event():
    """Executado ao encerrar a aplicação"""
    print(f"👋 Encerrando {settings.APP_NAME}")
