from fastapi import FastAPI


app = FastAPI()

# routing
# Get method  
@app.get()
def home():
    return {"message": "hello world!"}

