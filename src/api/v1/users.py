from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from jose import jwt
import uuid

from db.postgres import get_session
from core.config import settings
from schemas.entity import (
    UserUpdateLogin,
    UserInDB,
    LoginHistoryResponse,
    UserUpdatePassword,
)
from services.user_service import UserService
from services.auth_service import AuthService

router = APIRouter()

security = HTTPBearer(
    auto_error=False,
    description="Bearer токен для авторизации"
)


async def get_current_user_id(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> str:
    """
    Извлекает user_id из access token.
    """
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid Authorization header",
            headers={"WWW-Authenticate": "Bearer"},
        )
    token = credentials.credentials
    # Проверка черного списка
    if await AuthService.is_token_blacklisted(token):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token revoked",
            headers={"WWW-Authenticate": "Bearer"},
        )
    try:
        payload = jwt.decode(
            token,
            settings.secret_key,
            algorithms=[settings.algorithm]
        )
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )
        return user_id
    except jwt.JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )


@router.patch(
    "/me",
    response_model=UserInDB,
    status_code=status.HTTP_200_OK,
    summary="Обновление логина текущего пользователя",
    responses={
        200: {"description": "Логин успешно обновлен"},
        400: {"description": "Некорректные данные"},
        401: {"description": "Не авторизован"},
        404: {"description": "Пользователь не найден"},
        409: {"description": "Логин уже занят"},
    }
)
async def update_login(
    update_data: UserUpdateLogin,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_session)
) -> UserInDB:
    """
    Обновляет логин текущего пользователя.
    """
    return await UserService.update_login(
        user_id=user_id,
        update_data=update_data,
        db=db
    )


@router.patch(
    "/me/password",
    response_model=UserInDB,
    status_code=status.HTTP_200_OK,
    summary="Изменение пароля текущего пользователя",
    responses={
        200: {"description": "Пароль успешно изменен"},
        400: {"description": "Некорректные данные"},
        401: {"description": "Неверный текущий пароль или не авторизован"},
        404: {"description": "Пользователь не найден"},
    }
)
async def update_password(
    update_data: UserUpdatePassword,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_session)
) -> UserInDB:
    """
    Изменяет пароль текущего пользователя после проверки текущего пароля.
    """
    return await UserService.update_password(
        user_id=uuid.UUID(user_id),
        update_data=update_data,
        db=db
    )


@router.get(
    "/me/login-history",
    response_model=list[LoginHistoryResponse],
    status_code=status.HTTP_200_OK,
    summary="Получить историю входов текущего пользователя",
    responses={
        200: {"description": "История входов получена"},
        401: {"description": "Не авторизован"},
        404: {"description": "Пользователь не найден"},
    }
)
async def get_login_history(
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_session)
) -> list[LoginHistoryResponse]:
    """
    Возвращает историю входов текущего пользователя.
    """
    return await UserService.get_login_history(
        user_id=uuid.UUID(user_id),
        db=db
    )
