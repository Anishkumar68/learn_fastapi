## File Uploads in FastAPI: A Deep Dive

### Concept 1: Why Files Are Different (The Protocol)
When you send JSON to an API, the `Content-Type` is `application/json`. But files cannot be sent as JSON. Browsers and HTTP clients send files using a protocol called **`multipart/form-data`**. 

Because of this, **you cannot use Pydantic models to receive files**. Pydantic expects JSON. Instead, FastAPI provides two specific tools: `File` and `UploadFile`.

```python
from fastapi import UploadFile, File

# This tells FastAPI: "Expect a multipart form field named 'file'"
async def upload_file(file: UploadFile = File()):
    pass
```

### Concept 2: The `UploadFile` Object (Memory Management)
`UploadFile` is not just a simple string or byte array. It is a wrapper around a Python `SpooledTemporaryFile`. 

This is a critical architectural feature: **it does not load the entire file into RAM**. 
- If a user uploads a 2GB video, reading it all at once with `await file.read()` will crash your server by exhausting its memory.
- Instead, `UploadFile` writes the incoming data to a temporary file on your server's disk. Once it exceeds a certain size (usually 1MB), it spills over to disk automatically.
- You can read it in chunks, or copy it directly to its final destination without ever loading the whole thing into memory.

**Key properties of `UploadFile`:**
- `filename`: The original name of the file (e.g., `"my_photo.jpg"`). *Warning: Never trust this blindly.*
- `content_type`: The MIME type sent by the client (e.g., `"image/jpeg"`). *Warning: Clients can fake this.*
- `file`: The actual Python file-like object you can read from.
- `size`: The size of the file in bytes (available in newer FastAPI versions).

### Concept 3: Saving the File to Disk
To save an uploaded file, you need to read from the `UploadFile` and write it to your server's filesystem. Since we are building an async API, we should use an async file library to avoid blocking the event loop.

First, install the async file library:
```bash
pip install aiofiles
```

Then, the saving logic looks like this:

```python
import os
import uuid
import aiofiles
from fastapi import UploadFile, File, HTTPException, status
from pathlib import Path

# Define a safe directory for uploads
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True) # Create the directory if it doesn't exist

async def save_upload_file(upload_file: UploadFile) -> str:
    # 1. Generate a unique, safe filename to prevent collisions and directory traversal attacks
    # Example: "a1b2c3d4-e5f6.jpg"
    file_extension = Path(upload_file.filename).suffix
    unique_filename = f"{uuid.uuid4()}{file_extension}"
    file_path = UPLOAD_DIR / unique_filename

    # 2. Open the destination file in async write-binary mode ('wb')
    async with aiofiles.open(file_path, "wb") as out_file:
        # 3. Read the uploaded file in chunks (e.g., 8KB at a time)
        while content := await upload_file.read(8192):
            await out_file.write(content)

    # 4. Return the unique filename so we can save it to the database
    return unique_filename
```

### Concept 4: Security and Validation (The Trap)
This is where most beginners build vulnerable APIs. You must validate two things: **File Type** and **File Size**.

**Trap 1: Trusting `content_type`**
A malicious user can upload a malicious Python script (`virus.py`) but tell the browser its `content_type` is `"image/png"`. If you only check `content_type`, you will save the virus.

**The Fix:** Check the file extension against a strict allowlist.
```python
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif"}

file_extension = Path(upload_file.filename).suffix.lower()
if file_extension not in ALLOWED_EXTENSIONS:
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="File type not allowed. Only images are permitted."
    )
```

**Trap 2: Unlimited File Size**
If you don't limit file size, an attacker can send a 50GB file, filling up your server's hard drive (Denial of Service).

**The Fix:** Check the size before or during the read process.
```python
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 Megabytes

if upload_file.size and upload_file.size > MAX_FILE_SIZE:
    raise HTTPException(
        status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
        detail="File is too large. Maximum size is 5MB."
    )
```

### Concept 5: The Database Connection (The Real-World Pattern)
In a real application, you don't just save a file to a folder and forget about it. You need to link it to a database record. 

The industry standard pattern is:
1. Receive the `UploadFile`.
2. Validate its type and size.
3. Generate a unique filename (like a UUID).
4. Save the file to disk (or to cloud storage like AWS S3) using that unique name.
5. Save **only the unique filename or URL** as a string in your database model.

**Example Database Model:**
```python
class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(50))
    # Store the unique filename, NOT the file itself
    profile_image: Mapped[str | None] = mapped_column(String(255), nullable=True) 
```

**Example Route Putting It All Together:**
```python
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated
from pathlib import Path
import uuid
import aiofiles

router = APIRouter()

@router.post("/users/me/profile-picture")
async def upload_profile_picture(
    file: Annotated[UploadFile, File()],
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)]
):
    # 1. Validate Extension
    ext = Path(file.filename).suffix.lower()
    if ext not in {".jpg", ".jpeg", ".png"}:
        raise HTTPException(status_code=400, detail="Invalid file type")

    # 2. Validate Size (e.g., max 5MB)
    if file.size and file.size > 5 * 1024 * 1024:
        raise HTTPException(status_code=413, detail="File too large")

    # 3. Generate safe filename
    safe_filename = f"{uuid.uuid4()}{ext}"
    file_path = Path("uploads") / safe_filename

    # 4. Save to disk
    async with aiofiles.open(file_path, "wb") as out_file:
        while content := await file.read(8192):
            await out_file.write(content)

    # 5. Update the database with the new filename
    current_user.profile_image = safe_filename
    await db.commit()
    await db.refresh(current_user)

    return {"message": "File uploaded successfully", "filename": safe_filename}
```

### Concept 6: Serving the Uploaded Files
Once a file is saved, the frontend needs a way to display it. You have two main options:

1. **Static Files Mount (Simple)**: Tell FastAPI to serve a specific folder as static files.
   ```python
   from fastapi.staticfiles import StaticFiles
   from fastapi import FastAPI

   app = FastAPI()
   # Now any file in the "uploads" folder is accessible at http://localhost:8000/uploads/filename.jpg
   app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")
   ```
2. **Cloud Storage (Production)**: In production, you rarely serve files from your own server. Instead, you upload the file to AWS S3, Cloudflare R2, or similar, and save the public URL (e.g., `https://my-bucket.s3.amazonaws.com/uuid.jpg`) in your database.

