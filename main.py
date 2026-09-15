from http.client import HTTPException

from fastapi import FastAPI,status, Depends
from app.schema import Product, UserCreate, UserResponse

app = FastAPI()
users = [
    {"id" : 1, "name":"anish", "email": "anish@gmail.com"},
    {"id" : 2, "name":"ak", "email": "ak@gmail.com"}
]
# routing
# Get method  
@app.get('/')
def home():
    return {"message": "hello world!"}

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

@app.get("/products")
# import pydantic class use dot to access the validation 
def get_product(product:Product):
    return {
        "name": product.name,
        "price": product.price,
        "category": product.category
    }


@app.post("/users", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
# def create_users(user:User):
#     return {
#         "Name" : user.name,
#         "Email" : user.email,
#         "age" : user.age
#     }

def create_user(user:UserCreate):
    return user


#http exception
# @app.get("/user/{userid}")
# def get_user(userid:int):
#     for user in users:
#         if user["id"] == userid:
#             return user
#     raise HTTPException(Status_code = status.HTTP_404_NOT_FOUND, details = "user Not found")
            

# delete user
@app.delete("/delete/user/{userid}")
def remove_user(userid:int):
    for user in users:
        if user["id"] ==userid:
           user.remove(user)
           return {"message": "user removed successfully"}
    raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, details = "user Not found")

def get_user():
    return {
        "username": "ak",
        "email": "anish@gmail.com"
    }
# depends 
@app.get("/current/user")
def get_current_user(user = Depends(get_user)):
    return user