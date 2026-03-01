from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from asyncpg import UniqueViolationError
from fastapi import HTTPException, status

from models.entity import User
from schemas.entity import UserCreate, UserInDB


class AuthService:
    @staticmethod
    async def create_user(user_create: UserCreate,
                          db: AsyncSession) -> UserInDB:
        # Проверяем, существует ли пользователь с таким логином
        existing_user = await db.execute(
            User.__table__.select().where(User.login == user_create.login)
        )
        if existing_user.fetchone():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="User with this login already exists"
            )

        user = User(**user_create.dict())
        db.add(user)
        try:
            await db.commit()
        except IntegrityError as e:
            await db.rollback()
            if isinstance(e.orig, UniqueViolationError):
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="User with this login already exists"
                )
            raise e
        await db.refresh(user)
        return user
