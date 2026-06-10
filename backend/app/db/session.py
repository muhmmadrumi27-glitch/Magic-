from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings

engine = create_async_engine(settings.sqlalchemy_database_uri, future=True, echo=False)
AsyncSessionLocal = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False, autoflush=False)

async def get_db() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        yield session