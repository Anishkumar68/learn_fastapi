
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from Starlette.exceptions import HTTPException as StarletteHTTPException


from Models import models
from schema import schema
from database import get_db


router = APIRouter()


# Dependency for database session
DBsession = Annotated[Session, Depends(get_db)]



# CREATE USER
@router.post(
    "/users",
    response_model=schema.UserResponse,
    status_code=status.HTTP_201_CREATED
)
def create_user(
    user: schema.UserCreate,
    db: DBsession
):

    # Check whether username already exists
    result = db.execute(
        select(models.User).where(
            models.User.username == user.name
        )
    )

    existing_user_name = result.scalars().first()

    # Check whether email already exists
    result = db.execute(
        select(models.User).where(
            models.User.email == user.email
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
        email=user.email
        # Add other fields here if your User model has them
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


# Get single user
@router.get(
    "/user/{userid}",
    response_model=schema.UserResponse
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

