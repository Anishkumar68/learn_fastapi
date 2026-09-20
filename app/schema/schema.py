import datetime
from pydantic import BaseModel, ConfigDict, EmailStr, Field
from app.database import Base

class User(BaseModel):
    user_name:str
    email:EmailStr
    password:str

class UserResponse(BaseModel):
    user_name:str
    email:str

class PostBase(BaseModel):
    title:str=Field(min_length=1, max_length=100)
    email:EmailStr = Field(max_length=120)
