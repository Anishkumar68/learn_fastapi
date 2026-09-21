from http.client import HTTPException
import select
from typing import Annotated
from fastapi import FastAPI,status, Depends
from sqlalchemy.orm import Session
from sqlalchemy import select
from Starlette.exceptions import HTTPException as StarletteHTTPException


# project imports 
from app.Models import models
from app.schema import schema
from app.schema.schema import Product, UserCreate, UserResponse
from app.database import engine, get_db
from app.Models.models import Base


app = FastAPI()

# this make sure the sqlalchemy models are created in the database
Base.metadata.create_all(bind=engine)


# instead of writing duplicate session code we use Annotation Depends to get the session from the get_db function and pass it to the route function as a parameter.
DBsession = Annotated[Session, Depends(get_db)]



# routing
# Get method  
# @app.get('/')
# def home():
#     return {"message": "hello world!"}

# route url with parameters 
# @app.get("/user/{userid}")
# def get_user(userid:int):
#     return {"userid": userid}

# without pydantic url desgin using the function limit,offsetm category are e.g for paramets. 
# @app.get("/products")
# def get_product(category:str, limit:int = 10, offset:int = 0 ):
#     return {
#         "category" : category,
#         "limit": limit,
#         "offset" : offset
#     }

# @app.get("/products")
# # import pydantic class use dot to access the validation 
# def get_product(product:Product):
#     return {
#         "name": product.name,
#         "price": product.price,
#         "category": product.category
#     }


# @app.post("/users", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
# def create_users(user:User):
#     return {
#         "Name" : user.name,
#         "Email" : user.email,
#         "age" : user.age
#     }

# def create_user(user:UserCreate):
#     return user


#http exception
# @app.get("/user/{userid}")
# def get_user(userid:int):
#     for user in users:
#         if user["id"] == userid:
#             return user
#     raise HTTPException(Status_code = status.HTTP_404_NOT_FOUND, details = "user Not found")
            

# delete user
# @app.delete("/delete/user/{userid}")
# def remove_user(userid:int):
#     for user in users:
#         if user["id"] ==userid:
#            user.remove(user)
#            return {"message": "user removed successfully"}
#     raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, details = "user Not found")

# def get_user():
#     return {
#         "username": "ak",
#         "email": "anish@gmail.com"
#     }
# # depends 
# @app.get("/current/user")
# def get_current_user(user = Depends(get_user)):
#     return user



# get single post
#response_model means that will provide output, for that we created a pydantic schema 
# so we import that its name is schema(the file ).(for access we are using dot)PostResponse(the output provider class)

# create user
@app.post("/users", response_model=schema.UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(user:schema.UserCreate, db:DBsession):
    """
    execute() → runs the SQL query
    scalars() → extracts the User objects from the result
    first() → gets the first User
    """
    check_user_name = db.execute(select(models.user).where(models.User.username == user.name)).first()
    check_user_mail = db.execute(select(models.User).where(models.user.email == user.email)).first()
    existing_user_email = check_user_mail.scalars().first()
    existing_user_name = check_user_name.scalars().first()

    if existing_user_email and existing_user_name:
        raise StarletteHTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User already exist")
  
    new_user = models.User(**user.dict())

    if new_user:
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        raise StarletteHTTPException(status_code = status.HTTP_201_CREATED, detail = "User created successfully")

    return new_user


# get single user
@app.get("/user/{userid}", response_model=schema.UserResponse)
def get_user(userid:int, db:DBsession):
    result = db.execute(select(models.User).where(models.User.id == userid))
    user = result.scalars().first()

    if not user:
        raise StarletteHTTPException(status_code =status.HTTP_404_NOT_FOUND, detail = "user not found")

    return user

# get single post
@app.get("/posts/{postid}",response_model=schema.PostResponse)
def get_post(post_id:int, db:DBsession):
    result = db.execute(select(models.Post).where(models.Post.id==post_id))
    post = result.scalars().first()

    if not post:
        raise StarletteHTTPException(status_code = status.HTTP_404_NOT_FOUND, detail = "No post found")

    return post

