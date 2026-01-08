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
    Endpoint de login - Autentica usuário e retorna tokens JWT

    **Compatível com OAuth2** - usa dados de formulário (username/password)

    Retorna:
    - **access_token**: Token de curta duração para acesso à API (30 minutos)
    - **refresh_token**: Token de longa duração para obter novos access tokens (7 dias)
    - **token_type**: Sempre "bearer"

    Exemplo de uso:
    ```
    curl -X POST "http://localhost:8000/api/v1/auth/login" \\
         -H "Content-Type: application/x-www-form-urlencoded" \\
         -d "username=admin&password=admin123"
    ```
    """
    # Autentica usuário
    user = auth_service.authenticate_user(db, form_data.username, form_data.password)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Nome de usuário ou senha incorretos",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Conta de usuário está inativa"
        )

    # Cria tokens
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
    Atualiza access token usando um refresh token

    Use este endpoint quando o access token expirar para obter um novo
    sem exigir que o usuário faça login novamente.

    **Corpo da requisição:**
    ```json
    {
        "refresh_token": "seu_refresh_token_aqui"
    }
    ```

    **Retorna:**
    - Novo par de access_token e refresh_token
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Não foi possível validar o refresh token",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        # Decodifica e valida refresh token
        payload = decode_token(refresh_request.refresh_token)
        username: str = payload.get("sub")
        token_type: str = payload.get("type")

        if username is None or token_type != "refresh":
            raise credentials_exception

    except Exception:
        raise credentials_exception

    # Verifica se o usuário ainda existe e está ativo
    user = auth_service.get_user_by_username(db, username)

    if user is None or not user.is_active:
        raise credentials_exception

    # Cria novos tokens
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
    Obtém informações do usuário autenticado atual

    Requer access token válido no cabeçalho Authorization:
    ```
    Authorization: Bearer seu_access_token_aqui
    ```
    """
    return UserResponse.model_validate(current_user)
