# first operation with sqlalchemy

## Step 1 — Create a User in the database

You already have the SQLAlchemy model:

```python
class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    email: Mapped[str] = mapped_column(String(255))
```

Now we need to make this happen:

```text
POST /users
      ↓
Receive JSON
      ↓
Pydantic validates it
      ↓
Create SQLAlchemy User object
      ↓
Add to Session
      ↓
Commit
      ↓
User is permanently stored in SQLite
```

### The key concepts you need to learn

Before writing the code, understand these **4 operations**:

| Operation         | Meaning                                        |
| ----------------- | ---------------------------------------------- |
| `db.add()`        | Put the new object into the current DB session |
| `db.commit()`     | Actually save the transaction                  |
| `db.refresh()`    | Reload the object from DB, e.g. generated `id` |
| `Depends(get_db)` | Give the endpoint a database session           |

So your first task is:

> **Build `POST /users` yourself without copying the previous code.**

You already know the pieces:

* Pydantic → request validation
* SQLAlchemy `User` → database table/object
* `Depends(get_db)` → database session
* `db.add()` → stage object
* `db.commit()` → save
* `db.refresh()` → get updated DB data

**Don't look at the old implementation. Try constructing it from that logic.**

Once you get `POST /users` working and can see the row inside `app.db`, **then the next step is `GET /users`** — learning how to query the database with SQLAlchemy `select()`.

That's the correct progression: **Create → Read → Update → Delete**, not jumping randomly between FastAPI topics.
