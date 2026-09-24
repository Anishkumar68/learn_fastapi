from typing import Annotated

from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session

from app.Models import models
from app.database import engine, get_db
from app.Models.models import Base
from app.routes import posts
from app.routes import users

app = FastAPI()


# This makes sure the SQLAlchemy models are created in the database
Base.metadata.create_all(bind=engine)


# Instead of writing duplicate session code, we use Annotated + Depends
# to get the session from the get_db function.
DBsession = Annotated[Session, Depends(get_db)]


app.include_router(
    router=users.router,
    prefix="/api/users",
    tags=["users"]
)

app.include_router(
    router = posts.router,
    prefix="/api/posts",
    tags=["posts"]
)

app.include_router(
    router=auth.router,
    prefix="/api/users",
    tags=["auth"]
)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="127.0.0.1",
        port=8000,
        reload=True
    )