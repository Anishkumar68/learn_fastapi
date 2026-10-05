## Pagination: A Deep Dive

This is one of the most important performance concepts in backend development. Let's build it up from the ground up.

---

## Concept 1: The Problem (Why Pagination Exists)

Imagine your database has 50,000 posts. A user opens your app and the frontend calls `GET /posts`.

Without pagination, your route does this:

```python
@router.get("/posts")
async def get_posts(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Post))
    posts = result.scalars().all()  # Fetches ALL 50,000 posts
    return posts
```

**What happens:**
1. The database reads 50,000 rows from disk
2. SQLAlchemy converts all 50,000 rows into Python objects
3. Pydantic serializes all 50,000 objects into JSON
4. Your server sends a 50MB JSON response over the network
5. The frontend tries to render 50,000 items in the browser

**Result:** Your server runs out of memory, the response takes 30 seconds, and the user's browser crashes.

**The Solution:** Only fetch and return a small chunk of data at a time. This is pagination.

---

## Concept 2: The Two Approaches

There are two fundamentally different ways to paginate data. Understanding when to use which is a senior-level skill.

### Approach A: Offset/Limit Pagination (Page-Based)
This is what you see on most websites: "Page 1, Page 2, Page 3..."

```
GET /posts?skip=0&limit=10   → Posts 1-10 (Page 1)
GET /posts?skip=10&limit=10  → Posts 11-20 (Page 2)
GET /posts?skip=20&limit=10  → Posts 21-30 (Page 3)
```

**How it works:**
- `skip` (also called `offset`): "Skip the first N rows"
- `limit`: "Then give me the next N rows"

**Pros:**
- Simple to understand and implement
- Easy to jump to any page ("Go to page 50")
- Works well for admin dashboards and search results

**Cons:**
- Gets slower as you go deeper (page 1000 is slower than page 1)
- If new data is inserted while the user is browsing, items can shift between pages (duplicates or missing items)

### Approach B: Cursor-Based Pagination (Keyset)
This is what infinite-scroll apps use: Twitter, Instagram, TikTok.

```
GET /posts?cursor=null&limit=10   → First 10 posts
GET /posts?cursor=abc123&limit=10 → Next 10 posts after cursor
```

**How it works:**
- `cursor`: A reference point (usually the ID of the last item you saw)
- `limit`: How many items to fetch after that point

**Pros:**
- Consistently fast no matter how deep you go
- No duplicates or missing items when new data is inserted
- Perfect for infinite scroll

**Cons:**
- Can't jump to "Page 50" (you can only go forward/backward)
- More complex to implement
- Requires a sortable, unique column (like `id` or `created_at`)

---

## Concept 3: Offset/Limit Pagination (The Implementation)

Let's implement this properly. This is the approach you'll use 80% of the time.

### Step 1: The Query Parameters

```python
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import Annotated

router = APIRouter()

@router.get("/posts")
async def get_posts(
    skip: Annotated[int, Query(ge=0, description="Number of items to skip")] = 0,
    limit: Annotated[int, Query(ge=1, le=100, description="Max items to return")] = 10,
    db: Annotated[AsyncSession, Depends(get_db)] = None
):
```

**What's happening here:**
- `skip: int = 0` → Default is 0 (start from the beginning)
- `limit: int = 10` → Default is 10 items per page
- `Query(ge=0)` → `ge` means "greater than or equal to". Prevents negative skip values.
- `Query(le=100)` → `le` means "less than or equal to". Prevents someone from requesting `limit=999999` and crashing your server.

### Step 2: The Database Query

```python
    # Fetch the posts with offset and limit
    stmt = select(Post).offset(skip).limit(limit)
    result = await db.execute(stmt)
    posts = result.scalars().all()
    
    return posts
```

**What `.offset()` and `.limit()` do in SQL:**

```sql
-- skip=0, limit=10
SELECT * FROM posts LIMIT 10 OFFSET 0;

-- skip=10, limit=10
SELECT * FROM posts LIMIT 10 OFFSET 10;

-- skip=20, limit=10
SELECT * FROM posts LIMIT 10 OFFSET 20;
```

The database engine skips the first N rows and then returns the next N rows. Simple and efficient for small offsets.

### Step 3: The Total Count (So the Frontend Knows How Many Pages Exist)

The frontend needs to know the total number of posts so it can display "Page 1 of 500". This requires a separate query:

```python
    # Count total posts
    count_stmt = select(func.count()).select_from(Post)
    total_result = await db.execute(count_stmt)
    total = total_result.scalar()
```

**What `func.count()` does:**
It generates `SELECT COUNT(*) FROM posts`. This is a fast query that just counts rows without loading any actual data.

**Why `select_from(Post)`?**
Without it, SQLAlchemy might generate `SELECT count(*)` without a `FROM` clause, which would return 1 instead of the actual count.

### Step 4: The Paginated Response Schema

Don't just return a list of posts. Return a structured object that includes metadata:

```python
from pydantic import BaseModel
from typing import List, Generic, TypeVar

# Generic type so we can reuse this for Posts, Users, Comments, etc.
T = TypeVar("T")

class PaginatedResponse(BaseModel, Generic[T]):
    items: List[T]
    total: int
    skip: int
    limit: int
    has_next: bool
    has_prev: bool
```

**Why this structure?**
- `items`: The actual data for this page
- `total`: Total number of items in the database (so frontend can calculate total pages)
- `skip` and `limit`: Echo back what was requested (helpful for the frontend)
- `has_next` and `has_prev`: Boolean flags so the frontend knows whether to show "Next" or "Previous" buttons

### Step 5: Putting It All Together

```python
@router.get("/posts", response_model=PaginatedResponse[PostResponse])
async def get_posts(
    skip: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 10,
    db: Annotated[AsyncSession, Depends(get_db)] = None
):
    # 1. Fetch the paginated posts
    stmt = select(Post).offset(skip).limit(limit)
    result = await db.execute(stmt)
    posts = result.scalars().all()
    
    # 2. Count total posts
    count_stmt = select(func.count()).select_from(Post)
    total_result = await db.execute(count_stmt)
    total = total_result.scalar()
    
    # 3. Build and return the paginated response
    return PaginatedResponse(
        items=posts,
        total=total,
        skip=skip,
        limit=limit,
        has_next=(skip + limit) < total,
        has_prev=skip > 0
    )
```

### What the Client Receives

```json
{
  "items": [
    {"id": 1, "post_title": "First Post", ...},
    {"id": 2, "post_title": "Second Post", ...},
    ...
  ],
  "total": 50000,
  "skip": 0,
  "limit": 10,
  "has_next": true,
  "has_prev": false
}
```

The frontend can now:
- Display 10 posts
- Show "Page 1 of 5000" (calculated from `total / limit`)
- Enable/disable "Next" and "Previous" buttons based on `has_next` and `has_prev`

---

## Concept 4: The Performance Trap (Deep Offset)

Here's the critical thing most tutorials don't teach you.

When you request `skip=49990&limit=10` (page 5000), the database doesn't magically jump to row 49990. It actually:

1. Reads rows 1 through 49990
2. Throws them all away
3. Returns rows 49991 through 50000

This means **page 5000 is 500x slower than page 1**. For a table with millions of rows, deep pagination can take seconds.

### The Fix: Cursor-Based Pagination

Instead of saying "skip 49990 rows", you say "give me 10 rows where the ID is greater than 49990".

```python
@router.get("/posts")
async def get_posts_cursor(
    cursor: Annotated[int | None, Query(ge=0, description="Last seen post ID")] = None,
    limit: Annotated[int, Query(ge=1, le=100)] = 10,
    db: Annotated[AsyncSession, Depends(get_db)] = None
):
    stmt = select(Post).order_by(Post.id)
    
    if cursor is not None:
        # Only fetch posts with ID greater than the cursor
        stmt = stmt.where(Post.id > cursor)
    
    stmt = stmt.limit(limit)
    
    result = await db.execute(stmt)
    posts = result.scalars().all()
    
    # The new cursor is the ID of the last post returned
    next_cursor = posts[-1].id if posts else None
    
    return {
        "items": posts,
        "next_cursor": next_cursor,
        "has_next": len(posts) == limit
    }
```

**Why this is fast:**
The database uses the primary key index to jump directly to the row with `id > cursor`. It doesn't scan or skip any rows. Page 1 and page 5000 take the exact same amount of time.

**The tradeoff:**
- You can't jump to "Page 50" (no random access)
- The client must keep track of the `next_cursor` value
- You need a sortable, unique column (like `id` or `created_at`)

---

## Concept 5: When to Use Which

| Scenario | Use This | Why |
|----------|----------|-----|
| Admin dashboard with page numbers | Offset/Limit | Users need to jump to specific pages |
| Search results | Offset/Limit | Users expect page numbers |
| Infinite scroll feed (Twitter, Instagram) | Cursor | Consistent performance, no duplicates |
| Mobile app with "Load More" button | Cursor | Simple forward-only navigation |
| API consumed by other developers | Offset/Limit | Easier to understand and use |
| Table with millions of rows | Cursor | Offset becomes too slow |

---

## Concept 6: The Generic Paginated Response (Reusable)

Since you'll paginate posts, users, comments, and everything else, make the response schema generic so you write it once:

```python
from pydantic import BaseModel
from typing import List, Generic, TypeVar

T = TypeVar("T")

class PaginatedResponse(BaseModel, Generic[T]):
    items: List[T]
    total: int
    skip: int
    limit: int
    has_next: bool
    has_prev: bool
```

Now you can use it for anything:

```python
@router.get("/posts", response_model=PaginatedResponse[PostResponse])
async def get_posts(...):
    ...

@router.get("/users", response_model=PaginatedResponse[UserResponse])
async def get_users(...):
    ...

@router.get("/comments", response_model=PaginatedResponse[CommentResponse])
async def get_comments(...):
    ...
```

The `[PostResponse]` part tells Pydantic: "The `items` list contains `PostResponse` objects." This gives you proper type validation and Swagger documentation for each endpoint.

---

## Summary

| Concept | Key Takeaway |
|---------|-------------|
| Why paginate | Fetching all rows crashes your server and the client's browser |
| Offset/Limit | Simple, supports page numbers, gets slow at deep pages |
| Cursor-based | Always fast, no random access, perfect for infinite scroll |
| `func.count()` | Fast way to get total row count without loading data |
| `Query(ge=0, le=100)` | Validates and constrains pagination parameters |
| Generic response | Write the pagination schema once, reuse for every model |
| `has_next` / `has_prev` | Tells the frontend whether to show navigation buttons |

This covers the full conceptual and practical landscape of pagination in FastAPI. Let me know what topic you want to explore next.