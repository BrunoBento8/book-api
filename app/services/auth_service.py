from sqlalchemy.orm import Session
from sqlalchemy.exc import OperationalError, SQLAlchemyError
from typing import Optional
from app.models.user import User
from app.utils.security import verify_password
import logging
import time

logger = logging.getLogger(__name__)


class AuthService:
    """Service class for authentication-related operations"""

    @staticmethod
    def authenticate_user(db: Session, username: str, password: str) -> Optional[User]:
        """
        Authenticate a user by username and password

        Args:
            db: Database session
            username: Username
            password: Plain text password

        Returns:
            User object if authentication successful, None otherwise

        Raises:
            OperationalError: If database is locked or unavailable
            SQLAlchemyError: For other database errors
        """
        try:
            # Query user with retry logic for database locks
            max_retries = 3
            retry_delay = 0.1  # 100ms

            for attempt in range(max_retries):
                try:
                    user = db.query(User).filter(User.username == username).first()
                    break  # Success, exit retry loop
                except OperationalError as e:
                    if "database is locked" in str(e) and attempt < max_retries - 1:
                        logger.warning(f"Database locked on attempt {attempt + 1}, retrying...")
                        time.sleep(retry_delay)
                        retry_delay *= 2  # Exponential backoff
                    else:
                        raise  # Re-raise if not a lock error or out of retries

            if not user:
                logger.debug(f"User not found: {username}")
                return None

            # Verify password
            try:
                if not verify_password(password, user.hashed_password):
                    logger.debug(f"Password verification failed for user: {username}")
                    return None
            except Exception as e:
                logger.error(f"Password verification error for {username}: {e}")
                return None

            logger.debug(f"User authenticated successfully: {username}")
            return user

        except OperationalError as e:
            logger.error(f"Database operational error during authentication for {username}: {e}")
            raise

        except SQLAlchemyError as e:
            logger.error(f"Database error during authentication for {username}: {e}")
            raise

        except Exception as e:
            logger.error(f"Unexpected error during authentication for {username}: {e}")
            return None

    @staticmethod
    def get_user_by_username(db: Session, username: str) -> Optional[User]:
        """
        Get user by username

        Args:
            db: Database session
            username: Username to search for

        Returns:
            User object if found, None otherwise
        """
        try:
            return db.query(User).filter(User.username == username).first()
        except SQLAlchemyError as e:
            logger.error(f"Database error getting user by username {username}: {e}")
            raise

    @staticmethod
    def get_user_by_email(db: Session, email: str) -> Optional[User]:
        """
        Get user by email

        Args:
            db: Database session
            email: Email to search for

        Returns:
            User object if found, None otherwise
        """
        try:
            return db.query(User).filter(User.email == email).first()
        except SQLAlchemyError as e:
            logger.error(f"Database error getting user by email {email}: {e}")
            raise


# Create singleton instance
auth_service = AuthService()
