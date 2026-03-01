from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from db.postgres import get_session
from schemas.entity import UserCreate, UserInDB
from services.auth_service import AuthService

router = APIRouter()


@router.post(
    '/signup',
    response_model=UserInDB,
    status_code=status.HTTP_201_CREATED
)
async def create_user(
    user_create: UserCreate,
    db: AsyncSession = Depends(get_session)
) -> UserInDB:
    return await AuthService.create_user(user_create, db)
