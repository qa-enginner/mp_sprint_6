from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from typing import Annotated
from fastapi.encoders import jsonable_encoder
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from asyncpg import UniqueViolationError

from db.postgres import async_session, get_session
# from schemas.token import Token, TokenRefresh, TokenRevoke
# from core.security import (
#     create_access_token,
#     create_refresh_token,
#     verify_refresh_token
# )
# from services.auth import authenticate_user
from schemas.entity import UserCreate, UserInDB
from models.entity import User

router = APIRouter()


# @router.post("/login", response_model=Token)
# async def login_for_access_token(
#     form_data: Annotated[OAuth2PasswordRequestForm, Depends()]
# ):
#     """Аутентификация пользователя и выдача токенов"""
#     async with async_session() as session:
#         user = await authenticate_user(
#             session,
#             form_data.username,
#             form_data.password
#         )
#         if not user:
#             raise HTTPException(
#                 status_code=status.HTTP_401_UNAUTHORIZED,
#                 detail="Incorrect username or password",
#                 headers={"WWW-Authenticate": "Bearer"},
#             )

#         access_token = create_access_token(
#             data={"sub": user.login, "user_id": str(user.id)}
#         )
#         refresh_token = create_refresh_token(
#             data={"sub": user.login, "user_id": str(user.id)}
#         )

#         return Token(
#             access_token=access_token,
#             refresh_token=refresh_token,
#             token_type="bearer"
#         )


# @router.post("/refresh", response_model=Token)
# async def refresh_access_token(token_data: TokenRefresh):
#     """Обновление access токена с помощью refresh токена"""
#     try:
#         payload = verify_refresh_token(token_data.refresh_token)
#         user_id = payload.get("user_id")
#         username = payload.get("sub")

#         if user_id is None or username is None:
#             raise HTTPException(
#                 status_code=status.HTTP_401_UNAUTHORIZED,
#                 detail="Invalid refresh token",
#             )

#         access_token = create_access_token(
#             data={"sub": username, "user_id": user_id}
#         )
#         refresh_token = create_refresh_token(
#             data={"sub": username, "user_id": user_id}
#         )

#         return Token(
#             access_token=access_token,
#             refresh_token=refresh_token,
#             token_type="bearer"
#         )
#     except Exception:
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="Invalid refresh token",
#         )


# @router.post("/logout")
# async def revoke_token(token_data: TokenRevoke):
#     """Отзыв токена (выход из системы)"""
#     # В данной реализации токены отслеживаются в Redis
#     # Здесь можно добавить логику добавления токена в черный список
#     return {"message": "Successfully logged out"}


@router.post(
    '/signup',
    response_model=UserInDB,
    status_code=status.HTTP_201_CREATED
)
async def create_user(
    user_create: UserCreate,
    db: AsyncSession = Depends(get_session)
) -> UserInDB:
    user_dto = jsonable_encoder(user_create)
    user = User(**user_dto)
    db.add(user)
    try:
        await db.commit()
    except IntegrityError as e:
        if isinstance(e.orig, UniqueViolationError):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="User with this login already exists"
            )
        raise e
    await db.refresh(user)
    return user
