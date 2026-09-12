from fastapi import FastAPI,status
from models import Product, UserCreate, UserResponse

app = FastAPI()

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
