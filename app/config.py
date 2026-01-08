from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """Configurações da aplicação"""

    # Aplicação
    APP_NAME: str
    APP_VERSION: str
    ENVIRONMENT: str
    DEBUG: bool = False

    # Banco de Dados
    DATABASE_URL: str

    # Segurança
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # CORS
    ALLOWED_ORIGINS: List[str] = ["*"]

    # Admin (para inicialização)
    ADMIN_USERNAME: str = "admin"
    ADMIN_EMAIL: str = "admin@example.com"
    ADMIN_PASSWORD: str = "admin123"

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
