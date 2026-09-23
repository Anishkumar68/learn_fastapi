import datetime
from enum import unique
from pydantic import BaseModel, ConfigDict, EmailStr, Field
from rich.prompt import password
from app.database import Base

class UserBase(BaseModel):
    username:str=Field(min_length = 5, max_length=50)
    email : EmailStr = Field(max_length = 150)

class User(UserBase):
   id : int = Field(primary_key=True)
   username : str = Field(min_length=5, max_length=50)
   email : EmailStr = Field(max_length=150)
   password : str = Field(min_length=8, max_length=255, unique=True)
   user_created_at : datetime.datetime = Field(default_factory=datetime.datetime.utcnow)

class UserResponse(BaseModel):
    id : int
    username:str
    img_file : str | None
    img_path : str
    email : EmailStr
    model_config = ConfigDict(from_attributes = True)

class Userpublic(BaseModel):
    id:int
    username:str
    model_config = ConfigDict(from_attributes= True)

class Userprivate(BaseModel):
    email:EmailStr

class Userupdate(BaseModel):
    username:str
    email:EmailStr
    img_file:str|None
    img_path:str|None
    password : str|None

# schema for posts
class PostBase(BaseModel):
    title:str=Field(min_length=1, max_length=100)
    email:EmailStr = Field(max_length=120)

class PostCreate(PostBase):
    user_id:int
    content : str
    title : str
    
class PostResponse(PostBase):
    model_config = ConfigDict(from_attributes=True)
    id :int
    author: UserResponse

class Postupdate(PostBase):
    title : str | None = Field(default = None, min_length= 1, max_length=100)
    content :str|None = Field(default = None, min_length=1)

# auth token
class Token(BaseModel):
    access_token : str
    token_type: str
    