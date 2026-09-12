# fastapi learning

This is a learning project for FastAPI, a modern, fast (high-performance), web framework for building APIs with Python 3.6+ based on standard Python type hints.

pip install 'Fastapi[standard]'

only works with uv
uv run fastapi dev main.py

but we can also use
uvicorn main:app --reload [ for auto reload like in uv we have dev mode for auto reload]

## routing

@app
where the app come

we define a variable name app store fastapi()

```app = fastapi()```

---

**Note**: to hide any api route fastapi have a parameter for @app route in
Path parameter include_in_schema=bool

---

@app.get("/products/{product_id}")
def get_product(product_id: int):
/products/10

### Query parameter

```@app.get("/products")
def get_products(limit: int = 10):
/products?limit=10
```

### JSON:pydantic

Request body
class Product(BaseModel):
    name: str
    price: float
    category: str

@app.post("/products")
def create_product(product: Product):

```

{
    "name": "iPhone",
    "price": 79999,
    "category": "phone"
}

```

This distinction is fundamental to API development.
