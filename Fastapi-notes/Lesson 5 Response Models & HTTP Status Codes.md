
### 1. Response Model

Suppose our API creates a user.

```python
from pydantic import BaseModel


class UserCreate(BaseModel):
    name: str
    email: str
    age: int


class UserResponse(BaseModel):
    name: str
    email: str
```to hide any api route fastapi have a parameter for @app route in Path parameter include_in_schema=bool



Notice `UserResponse` doesn't have `age`.

Now:

```python
@app.post("/users", response_model=UserResponse)
def create_user(user: UserCreate):
    return user
```

The request can contain:

```json
{
    "name": "Ak",
    "email": "ak@example.com",
    "age": 25
}
```

But the response will be:

```json
{
    "name": "Ak",
    "email": "ak@example.com"
}
```

FastAPI uses `response_model` to **validate/filter the response**.

This is important in real applications because you don't want to accidentally return sensitive database fields such as:

```text
password
internal_id
secret_key
```

---

# 2. Request model vs Response model

A common production pattern is:

```python
class UserCreate(BaseModel):
    name: str
    email: str
    password: str


class UserResponse(BaseModel):
    name: str
    email: str
```

Why?

The client needs to **send** the password:

```text
Request
name
email
password
```

But shouldn't **receive** it:

```text
Response
name
email
```

So:

```text
UserCreate
   ↓
what client can SEND

UserResponse
   ↓
what client can RECEIVE
```

That's a very important API design concept.

---

# 3. HTTP Status Codes

An API response isn't just JSON.

It also has a **status code**.

Common ones:

| Code  | Meaning                   |
| ----- | ------------------------- |
| `200` | Successful request        |
| `201` | Successfully created      |
| `204` | Success, no response body |
| `400` | Bad request               |
| `401` | Not authenticated         |
| `403` | Forbidden                 |
| `404` | Resource not found        |
| `422` | Validation error          |
| `500` | Server error              |

For example, when creating a user, `201 Created` is more appropriate than the default `200`.

```python
from fastapi import FastAPI, status

app = FastAPI()


@app.post(
    "/users",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED
)
def create_user(user: UserCreate):
    return user
```

Now a successful request returns:

```text
201 Created
```

instead of:

```text
200 OK
```

---

# 4. Why status codes matter

Imagine:

```text
POST /users
```

Response:

```json
{
    "name": "Ak"
}
```

If you only look at the JSON, you don't know whether:

* user was created
* user already existed
* something went wrong

The status code communicates the result:

```text
201 → created successfully
400 → bad request
401 → authentication required
404 → resource doesn't exist
500 → server problem
```

Clients, frontend applications, monitoring systems, and other services depend on these codes.

---

## exercise

Create these two models:

```text
UserCreate
    name
    email
    password

UserResponse
    name
    email
```

Then create:

```text
POST /users
```

Requirements:

* Accept `UserCreate`
* Return `UserResponse`
* Return status code `201`

Test it through `/docs`.
