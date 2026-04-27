from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
    )

    database_url: str
    rabbitmq_url: str
    db_pool_size: int = Field(default=20, ge=1)
    db_max_overflow: int = Field(default=30, ge=0)
    db_pool_timeout: float = Field(default=30.0, ge=1.0)


@lru_cache
def get_settings() -> Settings:
    return Settings()
