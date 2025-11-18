# app/db/base.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

DATABASE_URL = "mysql+aiomysql://root:123456@127.0.0.1:33309/donate"

engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
# app/db/base.py (async SQLAlchemy setup)
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import declarative_base

# Use an async MySQL driver: aiomysql or asyncmy
# If you don't have aiomysql installed: pip install aiomysql
# DATABASE_URL = "mysql+aiomysql://root:123456@127.0.0.1:33309/hive_app"

# Create async engine
engine = create_async_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=3600,
    # echo = True,
    future=True,
)

# Async session factory
async_session = async_sessionmaker(
    bind=engine,
    expire_on_commit=False,
    autoflush=False,
    class_=AsyncSession,
)

# Declarative base for ORM models
Base = declarative_base()

from app.db.models.user import User


# FastAPI dependency helper
async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session() as session:
        yield session