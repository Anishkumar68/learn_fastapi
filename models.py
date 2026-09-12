from pydantic import BaseModel


class Product(BaseModel):
    name:str
    price:float
    category:str


class UserCreate(BaseModel):
    name:str
    email:str
    password:str

class UserResponse(BaseModel):
    user:str
    email:str


    