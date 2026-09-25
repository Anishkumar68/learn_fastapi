
import select

from fastapi import Depends
from fastapi.security import OAuth2PasswordRequestForm
from typing import Annotated
from rich_toolkit import form
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status
from starlette.exceptions import HTTPException as StarletteHTTPException
from Models import models
from auth.auth import create_access_token,verify_password

async def login_for_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()],db:str):
    result = await db.execute(
        select(models.User).where(
            func.lower(models.User.username) == form_data.username.lower()
        )
    )
    user = result.scalars().first()

    if not user or not verify_password(form_data.password, user.password_hash):
        raise StarletteHTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}


