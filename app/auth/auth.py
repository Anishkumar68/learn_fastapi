from datetime import UTC, timedelta, datetime
import select
from typing import Annotated
from fastapi import Depends, HTTPException
import jwt 
from fastapi.security import OAuth2PasswordBearer
from pwdlib import PasswordHash
from starlette import status
from starlette.exceptions import HTTPException as StarletteHTTPException
from app.database import get_db
from config import settings
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from Models.models import User

# Explicit PasswordHash initialization:
password_hash = PasswordHash.recommended()

# Token endpoint
oauth_schema = OAuth2PasswordBearer(tokenUrl="api/users/token")
DBsession = Annotated[AsyncSession, Depends(get_db)]

def hash_password(password:str):
    return password_hash.hash(password)

def verify_password(plain_password:str, hash_password:str)->bool:
    return password_hash.verify(plain_password, hash_password)


def create_access_token(data:dict, expires_delta:timedelta | None=None)->str:
    # payload data copy because we don't want to modify original data
    to_encode = data.copy()
    # check expires delta time if not 
    if not expires_delta:
        expire = datetime.now(UTC) + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE,
        )
        # if it have use that 
    else:
        expire= datetime.now(UTC) + expires_delta

    # Add exp in payload data . Jwt requires this field to know when to reject the token 
    to_encode.update({"exp":expire})
    # Finally we are creating a token using payload data, secret_key and algorithm
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY.get_secret_value(), algorithm=settings.algorithm)

    return encoded_jwt

def verify_access_token(token:str):
    try:
        payload = jwt.decode(
            token,
            settings.secret_key.get_secret_value(),
            algorithms= [settings.algorithm],
            options={"require":['exp','sub']},
        )
    except jwt.InvalidTokenError:
        return None
    else:
        return payload.get('sub')

def get_current_user(token:Annotated[str,Depends(oauth_schema)], db:DBsession):
    credentials_exception = StarletteHTTPException( status_code= status.HTTP_401_UNAUTHORIZED, detail="Unauthorized access", headers= {"WWW-Authenticate" : "Bearer"})

    try:

        payload = jwt.decode(
            token,
            settings.SECRET_KEY.get_secret_value(),
            algorithms=[settings.algorithm]
        )
        username: str=payload.get("sub")
        if username == None:
            raise credentials_exception
 
    except jwt.PyJWTError:
        raise credentials_exception

    result = db.execute(select(User).where(func.lower(User.username) == username))
    user = result.scalars().first()

    if user == None:
        raise credentials_exception
    
    return user
