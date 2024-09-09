from contextlib import asynccontextmanager

import sqlalchemy as sa
from pydantic import PostgresDsn
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.config import get_settings

settings = get_settings()

DEFAULT_DB_USER = settings.DEFAULT_DATABASE_USER
DEFAULT_DB_PASS = settings.DEFAULT_DATABASE_PASSWORD
DEFAULT_DB_HOST = settings.DEFAULT_DATABASE_HOSTNAME
DEFAULT_DB_PORT = settings.DEFAULT_DATABASE_PORT
DEFAULT_DB = settings.DEFAULT_DATABASE_DB
# SQLALCHEMY_DB_URL = settings.DEFAULT_SQLALCHEMY_DATABASE_URI


# SQLALCHEMY_DB_URL = f"postgresql+psycopg://{DEFAULT_DB_USER}:{DEFAULT_DB_PASS}@{DEFAULT_DB_HOST}:5432/{DEFAULT_DB}"
SQLALCHEMY_DB_URL: PostgresDsn = f"postgresql+psycopg://{DEFAULT_DB_USER}:{DEFAULT_DB_PASS}@{DEFAULT_DB_HOST}:5432/{DEFAULT_DB}"
echo = False

print(SQLALCHEMY_DB_URL)

engine = create_async_engine(
    settings.DB_CONFIG_PG.unicode_string(),
    echo=echo,
    pool_pre_ping=True,
    pool_recycle=280,
)
# async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

SessionLocal = async_sessionmaker(engine, autocommit=False, autoflush=False)

async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def get_db() -> AsyncSession:
    async with async_session() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

# metadata = sa.MetaData(schema="tenant")
Base = declarative_base()



