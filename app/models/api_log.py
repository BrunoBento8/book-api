from sqlalchemy import Column, Integer, String, Float, DateTime, Text
from datetime import datetime
from app.database import Base


class APILog(Base):
    """Modelo de log da API para monitoramento e analytics"""

    __tablename__ = "api_logs"

    id = Column(Integer, primary_key=True, index=True)
    endpoint = Column(String(200), nullable=False, index=True)
    method = Column(String(10), nullable=False)  # GET, POST, etc.
    status_code = Column(Integer, nullable=False)
    response_time = Column(Float, nullable=False)  # em milissegundos
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    user_id = Column(Integer, nullable=True)  # Para requisições autenticadas
    query_params = Column(Text, nullable=True)  # String JSON dos parâmetros de consulta
    error_message = Column(Text, nullable=True)  # Armazena detalhes de erro se houver

    def __repr__(self):
        return f"<APILog(id={self.id}, endpoint='{self.endpoint}', method='{self.method}', status={self.status_code})>"
