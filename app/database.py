from sqlalchemy import create_engine, event
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from app.config import settings
import logging

logger = logging.getLogger(__name__)

# Cria engine do SQLAlchemy com configurações otimizadas para concorrência
engine = create_engine(
    settings.DATABASE_URL,
    connect_args={
        "check_same_thread": False,  # Necessário para SQLite com múltiplas threads
        "timeout": 30  # Aumenta timeout de 5s para 30s para evitar database locks
    },
    poolclass=StaticPool,  # Usa pool estático para SQLite (melhor para single-file DB)
    echo=settings.DEBUG  # Loga todas as queries SQL em modo DEBUG
)

# Configura SQLite para modo WAL (Write-Ahead Logging) para melhor concorrência
# WAL permite leituras simultâneas mesmo durante escritas
@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_conn, connection_record):
    """
    Configura PRAGMAs do SQLite para melhor performance e concorrência.

    - journal_mode=WAL: Permite leituras concorrentes durante escritas
    - synchronous=NORMAL: Balance entre segurança e performance
    - foreign_keys=ON: Garante integridade referencial
    """
    cursor = dbapi_conn.cursor()
    cursor.execute("PRAGMA journal_mode=WAL")
    cursor.execute("PRAGMA synchronous=NORMAL")
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()
    logger.info("SQLite configured with WAL mode for better concurrency")

# Cria classe SessionLocal
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Cria classe Base para modelos
Base = declarative_base()


def get_db():
    """
    Dependência para sessões de banco de dados.
    Retorna uma sessão de banco de dados e a fecha quando concluída.

    Esta função é usada como dependência do FastAPI para injeção de sessões
    de banco de dados nos endpoints da API.
    """
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        logger.error(f"Database session error: {type(e).__name__}: {e}")
        db.rollback()
        raise
    finally:
        db.close()
