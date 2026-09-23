from datetime import UTC, timedelta, datetime

import jwt 
from fastapi.security import OAuth2PasswordBearer

from config import settings

class Authentication:

    token = datetime.utcnow() + datetime.timedelta(settings.ACCESS_TOKEN_EXPIRE)