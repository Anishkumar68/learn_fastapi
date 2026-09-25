from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated
from User.token import login_for_access_token
from app.database import get_db


router = APIRouter()
DBsession = Annotated[AsyncSession, Depends(get_db)]

@router.post("/token")
async def login_for_access_token(
    db: DBsession
):
    result = await login_for_access_token(db)
    return result