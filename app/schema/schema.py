from pydantic import BaseModel, ConfigDict


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


class PostCreate(BaseModel):
    post_title:str
    description:str
    context:str

class PostResponse(BaseModel):
    post_title:str
    description:str
    context:str
    owner_id:int

    model_config = ConfigDict(from_attributes=True)
    # (Note: from_attributes=True is the most important line here. It tells Pydantic, "Hey, I'm passing you a SQLAlchemy database object, not a dictionary. Read its attributes like post.id instead of post['id']".)
