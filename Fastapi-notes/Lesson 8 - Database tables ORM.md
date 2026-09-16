

```python
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    email: Mapped[str] = mapped_column(String(255))
```

Let's understand it from the bottom up.

---

# 1. What does this import mean?

```python
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
```

You're importing **three things from SQLAlchemy's ORM system**.

First understand ORM:

> **ORM = Object Relational Mapping**

It allows you to work with database tables using Python classes and objects.

Without ORM, you might write SQL:

```sql
SELECT * FROM users;
```

With SQLAlchemy ORM, you can work with:

```python
User
```

and:

```python
user = User(name="Ak", email="ak@gmail.com")
```

SQLAlchemy handles the translation between Python and the database.

---

# 2. `DeclarativeBase`

```python
DeclarativeBase
```

This is a SQLAlchemy class that provides the foundation for creating **declarative ORM models**.

That's why we do:

```python
class Base(DeclarativeBase):
    pass
```

Think of it as:

> "I'm creating the base class that all my database models will inherit from."

---

# 3. Why do we create `Base`?

This is the important part.

We could theoretically use `DeclarativeBase` directly, but instead we create our own:

```python
class Base(DeclarativeBase):
    pass
```

Now we have our project's common base:

```text
             DeclarativeBase
                    ↑
                    |
                   Base
                    ↑
          ┌─────────┴─────────┐
          │                   │
        User                Product
          │                   │
       users table        products table
```

Then:

```python
class User(Base):
```

means:

> `User` is a SQLAlchemy ORM model.

And later:

```python
class Product(Base):
```

means:

> `Product` is also a SQLAlchemy ORM model.

---

# 4. What does `pass` mean?

This:

```python
class Base(DeclarativeBase):
    pass
```

can look strange.

`pass` simply means:

> "I don't need to add anything else to this class right now."

We're creating `Base` mainly so our models can inherit from it.

You can think:

```python
class Base(DeclarativeBase):
    pass
```

as:

> "Create my project's SQLAlchemy base class."

Then:

```python
class User(Base):
```

says:

> "User is one of my database models."

---

# 5. Why does `User` need to inherit from `Base`?

This:

```python
class User(Base):
```

is extremely important.

Normal Python inheritance:

```python
class Animal:
    pass

class Dog(Animal):
    pass
```

`Dog` inherits from `Animal`.

Same idea:

```python
class Base(DeclarativeBase):
    pass

class User(Base):
    ...
```

`User` inherits from `Base`.

But here, `Base` gives SQLAlchemy the machinery needed to understand:

> "User is a database model and its attributes represent database columns."

Without that inheritance, SQLAlchemy doesn't treat an ordinary Python class as one of your declarative ORM models.

---

# 6. What is `Mapped`?

Now this:

```python
id: Mapped[int]
```

`Mapped` tells SQLAlchemy:

> "This Python attribute is mapped to something in the database."

And:

```python
Mapped[int]
```

means the Python-side value is an `int`.

So:

```python
id: Mapped[int]
```

means:

```text
id
 ↓
SQLAlchemy mapped attribute
 ↓
Python value is int
 ↓
Database column
```

Similarly:

```python
name: Mapped[str]
```

means:

> `name` is a mapped attribute containing a Python string.

---

# 7. What is `mapped_column`?

Now:

```python
id: Mapped[int] = mapped_column(primary_key=True)
```

There are actually **two pieces** here.

### Python type

```python
Mapped[int]
```

tells us:

> This attribute contains an integer.

### Database column configuration

```python
mapped_column(primary_key=True)
```

tells SQLAlchemy:

> Create/map this as a database column, and make it the primary key.

So the complete statement means:

> "Create a mapped database column called `id`, whose Python value is an integer, and make it the primary key."

---

# 8. Why not just use `int`?

You might ask:

Why not:

```python
id: int
```

Because that's just a **normal Python attribute/type annotation**.

SQLAlchemy needs to know:

> "This attribute represents a database column."

That's what:

```python
Mapped[int]
```

communicates to SQLAlchemy.

And:

```python
mapped_column(...)
```

provides the database-specific configuration.

---

# 9. Put everything together

Now read this:

```python
class User(Base):
```

Think:

> "User is a SQLAlchemy database model."

Then:

```python
__tablename__ = "users"
```

Think:

> "This model represents the `users` table."

Then:

```python
id: Mapped[int] = mapped_column(primary_key=True)
```

Think:

> "The table has an integer `id` column, and it's the primary key."

Then:

```python
name: Mapped[str] = mapped_column(String(100))
```

Think:

> "The table has a string `name` column with length 100."

Then:

```python
email: Mapped[str] = mapped_column(String(255))
```

Think:

> "The table has a string `email` column with length 255."

So SQLAlchemy understands approximately:

```text
users
┌────┬────────────┬─────────────────┐
│ id │ name       │ email           │
├────┼────────────┼─────────────────┤
│ 1  │ Ak         │ ak@gmail.com    │
│ 2  │ John       │ john@gmail.com  │
└────┴────────────┴─────────────────┘
```

---

# 10. The three imports — remember them like this

Don't memorize the definition. Remember their **jobs**:

```python
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
```

|Import|Think|
|---|---|
|`DeclarativeBase`|Foundation for our ORM models|
|`Mapped`|"This Python attribute is mapped to DB"|
|`mapped_column`|Defines/configures the DB column|

Then:

```python
class Base(DeclarativeBase):
    pass
```

means:

> **Create the common foundation for my database models.**

And:

```python
class User(Base):
```

means:

> **Make `User` a database model using that foundation.**

---

## One mental picture

This is the whole thing:

```text
SQLAlchemy
    │
    └── DeclarativeBase
             │
             ↓
        class Base(...)
             │
             │ inheritance
             ↓
        class User(Base)
             │
             ├── id     → mapped_column
             ├── name   → mapped_column
             └── email  → mapped_column
             │
             ↓
        Database table
            "users"
```

If you understand **this picture**, you don't need to memorize the code.

And this is why we're going slowly here: once you understand `Base → Model → Mapped → mapped_column`, the rest of SQLAlchemy becomes much easier.