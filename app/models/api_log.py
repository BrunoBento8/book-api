from sqlalchemy import Column, Integer, String, Float, DateTime, Text
from datetime import datetime
from app.database import Base


class APILog(Base):
    """API logging model for monitoring and analytics"""

    __tablename__ = "api_logs"

    id = Column(Integer, primary_key=True, index=True)
    endpoint = Column(String(200), nullable=False, index=True)
    method = Column(String(10), nullable=False)  # GET, POST, etc.
    status_code = Column(Integer, nullable=False)
    response_time = Column(Float, nullable=False)  # in milliseconds
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    user_id = Column(Integer, nullable=True)  # For authenticated requests
    query_params = Column(Text, nullable=True)  # JSON string of query parameters
    error_message = Column(Text, nullable=True)  # Store error details if any

    def __repr__(self):
        return f"<APILog(id={self.id}, endpoint='{self.endpoint}', method='{self.method}', status={self.status_code})>"
