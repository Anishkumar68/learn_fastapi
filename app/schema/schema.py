import datetime
from pydantic import BaseModel, ConfigDict, EmailStr, Field
from app.database import Base


class UserBase(BaseModel):
    username:str=Field(min_length = 5, max_length=50)
    email : EmailStr = Field(max_length = 150)
class User(UserBase):
   pass
class UserResponse(BaseModel):
    id = int
    img_file : str | None
    img_path : str

    model_config = ConfigDict(from_attributes = True)
class PostBase(BaseModel):
    title:str=Field(min_length=1, max_length=100)
    email:EmailStr = Field(max_length=120)

class PostCreate(PostBase):
    user_id:int
    
class PostResponse(PostBase):
    model_config = ConfigDict(from_attributes=True)
    id :int
    auther: UserResponse
