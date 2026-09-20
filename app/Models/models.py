from typing import Optional

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, Integer, String, Float, DateTime

from app.database import Base

class User(Base):
    __tablename__ = "users"

    id : Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    username :Mapped[str] = mapped_column(String(50), index = True)
    email : Mapped[str] = mapped_column(String(100))
    Password : Mapped[str] = mapped_column(String(50))
    posts : Mapped[list["Post"]] = relationship(back_populates="owner")

class Post(Base):
    __tablename__ = "posts"

    id : Mapped[int] = mapped_column(Integer, index=True)
    post_tile : Mapped[str] = mapped_column(String(100), nullable=False)
    description : Mapped[str] = mapped_column(String(100))
    context : Mapped[str] = mapped_column(String(1000))
    auther_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), index=True)
    date_posted:Mapped[DateTime] = mapped_column(DateTime, nullable=False)
    owner : Mapped["User"] = relationship(back_populates="posts")

class Comment(Base):
    __tablename__ = "comments"

    id : Mapped[int] = mapped_column(Integer, index=True, primary_key=True)
    comment : Mapped[str] = mapped_column(String(1000), nullable=False)
    post_id : Mapped[int] = mapped_column(Integer, ForeignKey("posts.id"), index=True)  
    reply_id : Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("comments.id"), index= True, nullable = True)
    reply_to : Mapped[Optional["Comment"]] = relationship("Comment", remote_side=[id], backref="replies")