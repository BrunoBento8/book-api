from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.auth import Token, RefreshTokenRequest, UserResponse
from app.services.auth_service import auth_service
from app.utils.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    get_current_user
)
from app.models.user import User

router = APIRouter()


@router.post("/auth/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """
    Login endpoint - Authenticate user and return JWT tokens

    **OAuth2 compatible** - uses form data (username/password)

    Returns:
    - **access_token**: Short-lived token for API access (30 minutes)
    - **refresh_token**: Long-lived token to obtain new access tokens (7 days)
    - **token_type**: Always "bearer"

    Example usage:
    ```
    curl -X POST "http://localhost:8000/api/v1/auth/login" \\
         -H "Content-Type: application/x-www-form-urlencoded" \\
         -d "username=admin&password=admin123"
    ```
    """
    # Authenticate user
    user = auth_service.authenticate_user(db, form_data.username, form_data.password)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive"
        )

    # Create tokens
    access_token = create_access_token(data={"sub": user.username})
    refresh_token = create_refresh_token(data={"sub": user.username})

    return Token(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer"
    )


@router.post("/auth/refresh", response_model=Token)
async def refresh_token(
    refresh_request: RefreshTokenRequest,
    db: Session = Depends(get_db)
):
    """
    Refresh access token using a refresh token

    Use this endpoint when the access token expires to get a new one
    without requiring the user to log in again.

    **Request body:**
    ```json
    {
        "refresh_token": "your_refresh_token_here"
    }
    ```

    **Returns:**
    - New access_token and refresh_token pair
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate refresh token",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        # Decode and validate refresh token
        payload = decode_token(refresh_request.refresh_token)
        username: str = payload.get("sub")
        token_type: str = payload.get("type")

        if username is None or token_type != "refresh":
            raise credentials_exception

    except Exception:
        raise credentials_exception

    # Verify user still exists and is active
    user = auth_service.get_user_by_username(db, username)

    if user is None or not user.is_active:
        raise credentials_exception

    # Create new tokens
    access_token = create_access_token(data={"sub": user.username})
    new_refresh_token = create_refresh_token(data={"sub": user.username})

    return Token(
        access_token=access_token,
        refresh_token=new_refresh_token,
        token_type="bearer"
    )


@router.get("/auth/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_user)
):
    """
    Get current authenticated user information

    Requires valid access token in Authorization header:
    ```
    Authorization: Bearer your_access_token_here
    ```
    """
    return UserResponse.model_validate(current_user)
