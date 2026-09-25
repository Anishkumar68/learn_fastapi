
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.orm import Session
from sqlalchemy import func, select
from starlette.exceptions import HTTPException as StarletteHTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from auth import (create_access_token,hash_password, verify_password, verify_access_token, oauth_password)
from Models import models
from schema.schema import UserBase,Usercreate,Userprivate,Userpublic,UserResponse,Userupdate

from database import get_db

from config import settings


from app.User.token import login_for_accerss_token

router = APIRouter()


# Dependency for database session
DBsession = Annotated[AsyncSession, Depends(get_db)]



# CREATE USER
@router.post(
    "/users",
    response_model= Userprivate,
    status_code=status.HTTP_201_CREATED
)
async def create_user(
    user: Usercreate,
    db: DBsession
):

    # Check whether username already exists
    result = await db.execute(
        select(models.User).where(
           func.lower( models.User.username) == user.name.lower(),
        )
    )

    existing_user_name = result.scalars().first()

    # Check whether email already exists
    result = db.execute(
        select(models.User).where(func.lower(
            models.User.email) == user.email.lower()
        )
    )

    existing_user_email = result.scalars().first()

    if existing_user_name or existing_user_email:
        raise StarletteHTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username or email already exists"
        )

    # Convert Pydantic schema to SQLAlchemy model
    new_user = models.User(
        username=user.name,
        email=user.email.lower(),
        # Add other fields here if your User model has them
        password_hash = hash_password(user.password)
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


# Get single user
@router.get(
    "/user/{userid}",
    response_model=UserResponse
)
def get_user(
    userid: int,
    db: DBsession
):

    result = db.execute(
        select(models.User).where(
            models.User.id == userid
        )
    )

    user = result.scalars().first()

    if not user:
        raise StarletteHTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    return user

