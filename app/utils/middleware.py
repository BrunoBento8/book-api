import time
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
from app.database import SessionLocal
from app.models.api_log import APILog
from datetime import datetime


class LoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware for logging all API requests and responses

    Logs:
    - Endpoint path
    - HTTP method
    - Response status code
    - Response time in milliseconds
    - Query parameters
    - Timestamp
    """

    def __init__(self, app: ASGIApp):
        super().__init__(app)

    async def dispatch(self, request: Request, call_next):
        # Start timer
        start_time = time.time()

        # Process request
        response: Response = await call_next(request)

        # Calculate response time
        response_time = (time.time() - start_time) * 1000  # Convert to milliseconds

        # Log to database (run in background to not block response)
        try:
            self.log_request(
                endpoint=str(request.url.path),
                method=request.method,
                status_code=response.status_code,
                response_time=response_time,
                query_params=str(dict(request.query_params)) if request.query_params else None
            )
        except Exception as e:
            # Don't fail the request if logging fails
            print(f"⚠️  Logging error: {e}")

        # Add response time header
        response.headers["X-Response-Time"] = f"{response_time:.2f}ms"

        return response

    def log_request(self, endpoint: str, method: str, status_code: int,
                    response_time: float, query_params: str = None):
        """Log request to database"""
        db = SessionLocal()
        try:
            log_entry = APILog(
                endpoint=endpoint,
                method=method,
                status_code=status_code,
                response_time=response_time,
                query_params=query_params,
                timestamp=datetime.utcnow()
            )
            db.add(log_entry)
            db.commit()
        except Exception as e:
            db.rollback()
            print(f"⚠️  Error saving log: {e}")
        finally:
            db.close()
