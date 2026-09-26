from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from typing import Annotated
from fastapi import Depends
from config import settings

# 1. Engine setup 
engine = create_async_engine(
    settings.DATABASE_URL, 
    connect_args={"check_same_thread": False}
)

# 2. Async Sessionmaker 
# async_sessionmaker
sessionLocal = async_sessionmaker(
    bind=engine, 
    expire_on_commit=False #for async to prevent lazy loading issues
)

# 3. Base Model 
class Base(DeclarativeBase):
    pass

# 4. Async Dependency 
async def get_db():
    async with sessionLocal() as session:
        yield session

# 5. FastAPI Usage 
# In your route:
# async def my_route(db: Annotated[AsyncSession, Depends(get_db)]):
#     ...
    # db = sessionLocal()

    # try:
    #     yield db
    # finally:
    #     db.close()