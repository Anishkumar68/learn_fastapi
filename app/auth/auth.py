from datetime import UTC, timedelta, datetime
import jwt 
from fastapi.security import OAuth2PasswordBearer
from pwdlib import PasswordHash
from config import settings

# Explicit PasswordHash initialization:
password_hash = PasswordHash.recommended()

# Token endpoint
oauth_password = OAuth2PasswordBearer(tokenUrl="api/users/token")

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


def create_access(data:dict, expire_delta:timedelta):
    to_encode = data.copy()
    if not expire_delta:
        expire = datetime.now(UTC) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE)
    else:
        expire = datetime.now(UTC) + expire_delta

    to_encode.update({"exp":expire})
    jwt_encode = jwt.encode(to_encode, settings.SECRET_KEY.get_secret_value(),algorithm=settings.algorithm)
    return jwt_encode


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