from pydantic import env_settings
from pydantic_settings import BaseSettings, SettingsConfigDict

from app.database import DATABASE_URL


class Settings(BaseSettings):
    SECRET_KEY : str
    DATABASE_URL : str 
    ACCESS_TOKEN_EXPIRE : int = 30

    model_config = {
        "env_file" : ".env"
    } 


settings = Settings()
