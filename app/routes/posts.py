from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.Models import models
from app.schema import schema
from app.schema.schema import PostCreate
from app.database import get_db

from Starlette.exceptions import HTTPException as StarletteHTTPException

router = APIRouter()

DBsession = Annotated[Session, Depends(get_db)]


# Get single post
@router.get("/{post_id}", response_model=schema.PostResponse)
def get_post(post_id: int, db: DBsession):

    result = db.execute(
        select(models.Post).where(models.Post.id == post_id)
    )

    post = result.scalars().first()

    if not post:
        raise StarletteHTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No post found"
        )

    return post


# Update full post
@router.put("/{post_id}", response_model=schema.PostResponse)
def update_post(
    post_id: int,
    post_data: PostCreate,
    db: DBsession
):

    result = db.execute(
        select(models.Post).where(models.Post.id == post_id)
    )

    post = result.scalars().first()

    if not post:
        raise StarletteHTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found"
        )

    # Check whether user exists
    if post_data.user_id != post.author_id:

        result = db.execute(
            select(models.User).where(
                models.User.id == post_data.user_id
            )
        )

        user = result.scalars().first()

        if not user:
            raise StarletteHTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

    # Actually update the database object
    post.title = post_data.title
    post.content = post_data.content
    post.author_id = post_data.user_id

    db.commit()
    db.refresh(post)

    return post


# Partial update
@router.patch(
    "/{post_id}",
    response_model=schema.PostResponse
)
def update_post_partial(
    post_id: int,
    post_data: schema.Postupdate,
    db: DBsession
):

    post = db.get(models.Post, post_id)

    if not post:
        raise StarletteHTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found"
        )

    # Only fields supplied by the client are included
    update_data = post_data.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(post, field, value)

    db.commit()
    db.refresh(post)

    return post


# Delete post
@router.delete(
    "/{post_id}",
    status_code=status.HTTP_204_NO_CONTENT
)
def delete_post(
    post_id: int,
    db: DBsession
):

    post = db.get(models.Post, post_id)

    if not post:
        raise StarletteHTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found"
        )

    db.delete(post)
    db.commit()

    return None