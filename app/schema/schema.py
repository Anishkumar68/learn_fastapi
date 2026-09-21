import datetime
from pydantic import BaseModel, ConfigDict, EmailStr, Field
from app.database import Base

class UserBase(BaseModel):
    username:str=Field(min_length = 5, max_length=50)
    email : EmailStr = Field(max_length = 150)

class User(UserBase):
   id : int = Field(primary_key=True)
   username : str = Field(min_length=5, max_length=50)
   email : EmailStr = Field(max_length=150)
   password : str = Field(min_length=8, max_length=100)
   user_created_at : datetime.datetime = Field(default_factory=datetime.datetime.utcnow)

class UserResponse(BaseModel):
    id : int
    img_file : str | None
    img_path : str
    email : EmailStr
    model_config = ConfigDict(from_attributes = True)

class PostBase(BaseModel):
    title:str=Field(min_length=1, max_length=100)
    email:EmailStr = Field(max_length=120)

class PostCreate(PostBase):
    user_id:int
    
class PostResponse(PostBase):
    model_config = ConfigDict(from_attributes=True)
    id :int
    author: UserResponse
