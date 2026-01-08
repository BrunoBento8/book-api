from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.config import settings

# Cria engine do SQLAlchemy
engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False}  # Necessário para SQLite
)

# Cria classe SessionLocal
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Cria classe Base para modelos
Base = declarative_base()


def get_db():
    """
    Dependência para sessões de banco de dados.
    Retorna uma sessão de banco de dados e a fecha quando concluída.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
