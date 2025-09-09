"""
Модуль для настройки подключения к базе данных с использованием SQLAlchemy и asyncpg.
"""
import os
from sqlmodel import SQLModel
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://postgres:postgres@db:5432/postgres")

# Async движок используя asyncpg
engine = create_async_engine(DATABASE_URL, echo=True, future=True)

# Фабрика сессий
async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


# Функция инициализации БД (создание таблиц)
async def init_db() -> None:
    """
    Создаёт таблицы (вызывается при старте приложения).
    """
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)


# Зависимость для получения сессии (для FastAPI Depends)
async def get_session():
    async with async_session() as session:
        yield session
