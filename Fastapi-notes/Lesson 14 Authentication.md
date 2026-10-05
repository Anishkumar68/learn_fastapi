**Topic 1:** Password Hashing with pwdlib[argon2] (what we're doing now) **Topic 2:** Configuration Management with pydantic-settings **Topic 3:** JWT Token Creation & Validation with pyjwt **Topic 4:** The Login Endpoint **Topic 5:** The get_current_user Dependency **Topic 6:** Protecting Routes **Topic 7:** Authorization Checks


You're absolutely right. Let me restart authentication properly, focused only on auth, broken into clear topics.

Here's our authentication roadmap:

**Topic 1:** Password Hashing with pwdlib[argon2] (what we're doing now)
**Topic 2:** Configuration Management with pydantic-settings
**Topic 3:** JWT Token Creation & Validation with pyjwt
**Topic 4:** The Login Endpoint
**Topic 5:** The get_current_user Dependency
**Topic 6:** Protecting Routes
**Topic 7:** Authorization Checks

Let's start with Topic 1.

---

## Topic 1: Password Hashing

### The Problem

When a user registers, they send you a password. You need to store it in the database. But storing plain passwords is a security disaster. If your database is hacked, all user accounts are compromised.

### The Solution: Hashing

Hashing is a one-way transformation. You can turn a password into a hash, but you can't turn a hash back into a password.

```
"mypassword123" → "$argon2id$v=19$m=65536,t=3,p=4$..."
```

When the user logs in, you hash the password they provide and compare it to the stored hash.

### The Tool: pwdlib with Argon2

`pwdlib` is a modern password hashing library created by the same person who made FastAPI. Argon2 is the most secure hashing algorithm (won the Password Hashing Competition in 2015).

**Install it:**
```bash
pip install pwdlib[argon2]
```

**The code:**
```python
from pwdlib import PasswordHash

# Create a hasher instance (uses argon2 by default)
ph = PasswordHash.new()

def hash_password(password: str) -> str:
    """Convert a plain password to a hash"""
    return ph.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Check if a plain password matches a hash"""
    return ph.verify(hashed_password, plain_password)
```

### How It Works

**User Registration:**
```python
# User sends: {"username": "john", "password": "mypassword123"}

# You hash the password
hashed = hash_password("mypassword123")
# hashed = "$argon2id$v=19$m=65536,t=3,p=4$abc123..."

# You store the HASH in the database, NOT the plain password
db_user = User(
    username="john",
    email="john@example.com",
    hashed_password=hashed  # Store the hash
)
db.add(db_user)
db.commit()
```

**User Login:**
```python
# User sends: {"username": "john", "password": "mypassword123"}

# You fetch the user from the database
user = db.query(User).filter(User.username == "john").first()

# You verify the password
is_valid = verify_password("mypassword123", user.hashed_password)
# is_valid = True

# If valid, proceed to create a token
# If invalid, return an error
```

### Why Argon2?

Argon2 has three variants:
- **Argon2d**: Fast, but vulnerable to side-channel attacks
- **Argon2i**: Slower, but resistant to side-channel attacks
- **Argon2id**: Hybrid (recommended) - best of both worlds

`pwdlib` uses Argon2id by default, which is the most secure choice.

### Important: Update Your User Model

Your current User model has a `Password` field. You need to change it to `hashed_password` and make it longer (Argon2 hashes are around 100 characters):

```python
class User(Base):
    __tablename__ = "users"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    username: Mapped[str] = mapped_column(String(50), index=True)
    email: Mapped[str] = mapped_column(String(100), unique=True)
    
    # CHANGED: From Password to hashed_password, and increased length
    hashed_password: Mapped[str] = mapped_column(String(255))
    
    posts: Mapped[list["Post"]] = relationship(back_populates="owner")
```

---

## challenge

Before we move to Topic 2 (Configuration Management), make sure you understand:

1. Why we hash passwords instead of storing them in plain text
2. How `hash_password()` and `verify_password()` work
3. That you need to update your User model to use `hashed_password` instead of `Password`

Great. Let's move to Topic 2.

---

## Topic 2: Configuration Management with pydantic-settings

### The Problem

Your authentication system needs sensitive values:

- `SECRET_KEY` — used to sign JWT tokens
- `DATABASE_URL` — your database connection string
- `ACCESS_TOKEN_EXPIRE_MINUTES` — how long tokens last

The **worst** thing you can do is hardcode these in your code:

```python
# NEVER DO THIS
SECRET_KEY = "my-super-secret-key-123"
DATABASE_URL = "postgresql://user:password@localhost/mydb"
```

**Why this is dangerous:**
1. If you push this to GitHub, your secrets are public forever
2. If someone forks your repo, they have your database password
3. You can't change values between development and production without editing code

### The Solution: Environment Variables

Environment variables are key-value pairs that live **outside** your code, in your operating system. Your code reads them at runtime.

```bash
# These live in your terminal/server, NOT in your code
export SECRET_KEY="my-super-secret-key-123"
export DATABASE_URL="postgresql://user:password@localhost/mydb"
```

But managing environment variables manually is annoying. That's where `.env` files and `pydantic-settings` come in.

### The Tool: pydantic-settings

`pydantic-settings` reads environment variables (or a `.env` file) and validates them using Pydantic. It's like a Pydantic model, but for your app's configuration.

**Install it:**
```bash
pip install pydantic-settings
```

### Step 1: Create a `.env` File

Create a file called `.env` in your project root:

```bash
# .env
SECRET_KEY=your-super-secret-key-change-this-in-production
DATABASE_URL=sqlite:///./my_database.db
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

**CRITICAL:** Add `.env` to your `.gitignore` file so it never gets pushed to GitHub:

```bash
# .gitignore
.env
```

### Step 2: Create the Settings Class

```python
# config.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # These fields will be automatically loaded from .env or environment variables
    SECRET_KEY: str
    DATABASE_URL: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30  # Has a default value

    # Tell pydantic-settings where to find the .env file
    model_config = {
        "env_file": ".env"
    }

# Create a single instance that you import everywhere
settings = Settings()
```

**What happens when you run `Settings()`:**
1. It looks for a `.env` file
2. It reads `SECRET_KEY`, `DATABASE_URL`, and `ACCESS_TOKEN_EXPIRE_MINUTES`
3. It validates them (e.g., `ACCESS_TOKEN_EXPIRE_MINUTES` must be an integer)
4. If a required field is missing, it raises an error immediately (fail fast!)

### Step 3: Use It Everywhere

Now, instead of hardcoding values, you import `settings`:

```python
# database.py
from config import settings
from sqlalchemy import create_engine

# Uses the DATABASE_URL from .env
engine = create_engine(settings.DATABASE_URL)
```

```python
# auth.py
from config import settings
import jwt

def create_access_token(data: dict) -> str:
    # Uses SECRET_KEY and ACCESS_TOKEN_EXPIRE_MINUTES from .env
    expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode = {"exp": expire, **data}
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm="HS256")
```

### Why This Is Powerful

**1. Type Validation:**
```python
# If someone puts this in .env:
ACCESS_TOKEN_EXPIRE_MINUTES=not_a_number

# pydantic-settings will crash immediately with a clear error:
# ValidationError: ACCESS_TOKEN_EXPIRE_MINUTES should be a valid integer
```

**2. Required vs Optional:**
```python
class Settings(BaseSettings):
    SECRET_KEY: str          # Required - app crashes if missing
    DATABASE_URL: str        # Required - app crashes if missing
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30  # Optional - defaults to 30
```

**3. Environment Override:**
Environment variables override `.env` file values. This is perfect for production:

```bash
# .env file says:
DATABASE_URL=sqlite:///./my_database.db

# But in production, you set an environment variable:
export DATABASE_URL=postgresql://user:pass@production-server/db

# pydantic-settings will use the environment variable (production)
# and ignore the .env file value
```

### Your Project Structure Now

```
my_project/
├── .env                    # Secrets (NEVER push to GitHub)
├── .gitignore              # Contains ".env"
├── config.py               # Settings class
├── main.py
├── database.py             # Uses settings.DATABASE_URL
├── auth.py                 # Uses settings.SECRET_KEY
├── models.py
├── schemas.py
└── routers/
    ├── users.py
    └── posts.py
```

---

## Summary of Topic 2

| Concept | What It Does |
|---------|-------------|
| `.env` file | Stores secrets locally, outside your code |
| `.gitignore` | Prevents `.env` from being pushed to GitHub |
| `pydantic-settings` | Reads `.env`, validates types, provides defaults |
| `settings` instance | Single object you import everywhere |
| Environment variables | Override `.env` values in production |

---

## Before We Move On

Make sure you understand:
1. Why we never hardcode secrets in code
2. How `.env` + `.gitignore` keeps secrets safe
3. How `pydantic-settings` reads and validates configuration
4. How to use `settings.SECRET_KEY` and `settings.DATABASE_URL` in your code

| ==NOTE: for login please check code better understanding 
