# db/postgres.py
from core.config import settings
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession

# Создаём базовый класс для будущих моделей
Base = declarative_base()
# Создаём движок
# Настройки подключения к БД передаём из переменных окружения,
# которые заранее загружены в файл настроек
dsn = (
    f'postgresql+asyncpg://'
    f'{settings.postgres_user}:'
    f'{settings.postgres_password}@'
    f'{settings.postgres_host}:'
    f'{settings.postgres_port}/'
    f'{settings.postgres_db}'
)
engine = create_async_engine(dsn, echo=True, future=True)
async_session = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)


async def create_database() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def purge_database() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


# Функция понадобится при внедрении зависимостей
# Dependency
async def get_session() -> AsyncSession:
    async with async_session() as session:
        yield session
