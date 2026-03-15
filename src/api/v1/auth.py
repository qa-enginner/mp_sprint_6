from fastapi import APIRouter, Depends, Request, status, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession

from db.postgres import get_session
from schemas.entity import (
        UserCreate,
        UserInDB,
        UserLogin,
        TokenResponse,
        TokenRefresh
    )
from services.auth_service import AuthService

router = APIRouter()

security = HTTPBearer(
    auto_error=False,  # Не выдавать ошибку автоматически
    description="Bearer токен для авторизации"
)


@router.post(
    '/register',
    response_model=UserInDB,
    status_code=status.HTTP_201_CREATED
)
async def create_user(
    user_create: UserCreate,
    db: AsyncSession = Depends(get_session)
) -> UserInDB:
    return await AuthService.create_user(user_create, db)


@router.post(
    '/login',
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK
)
async def login(
    request: Request,
    login_data: UserLogin,
    db: AsyncSession = Depends(get_session)
):
    return await AuthService.login(login_data, request, db)


@router.post(
    '/refresh',
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK
)
async def refresh(
    request: Request,
    token_refresh: TokenRefresh,
    db: AsyncSession = Depends(get_session)
):
    return await AuthService.refresh_token(
        token_refresh.refresh_token, request, db
    )


@router.post(
    '/logout',
    status_code=status.HTTP_200_OK,
    summary="Выход из системы",
    responses={
        200: {"description": "Успешный выход"},
        401: {"description": "Не авторизован или неверный токен"}
    }
)
async def logout(
    request: Request,
    token_refresh: TokenRefresh,
    credentials: HTTPAuthorizationCredentials = Depends(security)
    # db: AsyncSession = Depends(get_session)
):

    # Извлекаем access token из заголовка Authorization
    # credentials уже содержит токен от Depends(security)
    if credentials is None:
        # Если auto_error=False, нужно проверить наличие credentials
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Missing or invalid Authorization header",
                headers={"WWW-Authenticate": "Bearer"},
            )
        access_token = auth_header.split(" ")[1].strip()
    else:
        # Токен получен через Depends(security)
        access_token = credentials.credentials

    if not access_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Access token missing",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return await AuthService.logout(access_token, token_refresh.refresh_token)
