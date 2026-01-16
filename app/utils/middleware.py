import time
import asyncio
import logging
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
from app.database import SessionLocal
from app.models.api_log import APILog
from datetime import datetime
from sqlalchemy.exc import OperationalError

logger = logging.getLogger(__name__)


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

    Important: Logging is done asynchronously after response is sent
    to avoid blocking the request/response cycle and prevent database locks.
    """

    def __init__(self, app: ASGIApp):
        super().__init__(app)

    async def dispatch(self, request: Request, call_next):
        # Start timer
        start_time = time.time()

        # Process request FIRST - let it complete before logging
        response: Response = await call_next(request)

        # Calculate response time
        response_time = (time.time() - start_time) * 1000  # Convert to milliseconds

        # Add response time header
        response.headers["X-Response-Time"] = f"{response_time:.2f}ms"

        # Log to database asynchronously (doesn't block response)
        # Run in background task to completely isolate from request handling
        asyncio.create_task(
            self._log_request_async(
                endpoint=str(request.url.path),
                method=request.method,
                status_code=response.status_code,
                response_time=response_time,
                query_params=str(dict(request.query_params)) if request.query_params else None
            )
        )

        return response

    async def _log_request_async(self, endpoint: str, method: str, status_code: int,
                                  response_time: float, query_params: str = None):
        """
        Log request to database asynchronously in background.

        This method runs completely separately from the request/response cycle,
        preventing any database locks from affecting API responses.
        """
        # Small delay to ensure response is fully sent before we touch the database
        await asyncio.sleep(0.01)

        db = None
        try:
            # Create isolated database session
            db = SessionLocal()

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

        except OperationalError as e:
            # Database lock or connection error
            logger.warning(f"Database locked while logging request to {endpoint}: {e}")
            if db:
                db.rollback()
        except Exception as e:
            # Other unexpected errors - log but don't crash
            logger.error(f"Error saving API log for {endpoint}: {type(e).__name__}: {e}")
            if db:
                db.rollback()
        finally:
            if db:
                db.close()
