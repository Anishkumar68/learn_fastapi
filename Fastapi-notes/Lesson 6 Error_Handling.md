
## 1. The problem

Suppose we have:

```python
users = [
    {"id": 1, "name": "Ak"},
    {"id": 2, "name": "Rahul"},
]
```

And our endpoint:

```python
@app.get("/users/{user_id}")
def get_user(user_id: int):
    for user in users:
        if user["id"] == user_id:
            return user

    return {"message": "User not found"}
```

This technically works, but there's a problem.

If the user doesn't exist, we're still returning:

```text
200 OK
```

That's wrong.

A missing resource should normally return:

```text
404 Not Found
```

---

# 2. `HTTPException`

FastAPI provides:

```python
from fastapi import HTTPException
```

Then:

```python
@app.get("/users/{user_id}")
def get_user(user_id: int):

    for user in users:
        if user["id"] == user_id:
            return user

    raise HTTPException(
        status_code=404,
        detail="User not found"
    )
```

Now:

```text
GET /users/1
```

returns:

```text
200 OK
```

But:

```text
GET /users/99
```

returns:

```text
404 Not Found
```

with:

```json
{
    "detail": "User not found"
}
```

---

# 3. Why `raise`, not `return`?

This is important.

You might think:

```python
return HTTPException(...)
```

But that's wrong.

You use:

```python
raise HTTPException(...)
```

Because you're saying:

> Stop executing this endpoint and tell FastAPI that an HTTP error occurred.

Flow:

```text
Request
   ↓
get_user()
   ↓
user doesn't exist
   ↓
raise HTTPException
   ↓
FastAPI handles it
   ↓
404 response
```

---

# 4. Use status constants

Instead of:

```python
status_code=404
```

you can use:

```python
from fastapi import HTTPException, status
```

Then:

```python
raise HTTPException(
    status_code=status.HTTP_404_NOT_FOUND,
    detail="User not found"
)
```

This is more readable in larger projects.

---

# 5. Path validation vs business errors

There's an important distinction.

If you request:

```text
/users/abc
```

and your endpoint says:

```python
user_id: int
```

FastAPI handles the **type validation**.

You'll get a `422` validation response.

But if you request:

```text
/users/999
```

and `999` simply doesn't exist, that's **your application's business logic**.

You handle it:

```python
raise HTTPException(
    status_code=404,
    detail="User not found"
)
```

So:

```text
/users/abc
     ↓
Invalid type
     ↓
FastAPI validation
     ↓
422
```

versus:

```text
/users/999
     ↓
Valid integer
     ↓
Your database/business logic
     ↓
User doesn't exist
     ↓
404
```

That's an important distinction for interviews.

---

# Your exercise

Create:

```python
users = [
    {"id": 1, "name": "Ak"},
    {"id": 2, "name": "John"},
]
```

Then create:

```text
GET /users/{user_id}
```

Requirements:

* `user_id` must be `int`
* Return the user if found
* If not found, raise `HTTPException`
* Return `404`
* Message should be `"User not found"`

### Don't copy the previous solution

Write it yourself and send me the code. I'll check it, then we'll move to **CRUD + in-memory storage**, where the previous concepts finally start coming together.
