from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

from app.database import DATABASE_URL


class Settings(BaseSettings):
    SECRET_KEY : SecretStr
    DATABASE_URL : str        
    ACCESS_TOKEN_EXPIRE : int = 30
    algorithm : str = "HS256"

    model_config = SettingsConfigDict(
        env_file = ".env",
        env_file_encoding="utf-8"
    )


settings = Settings()
