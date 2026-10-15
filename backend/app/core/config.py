from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    project_name: str = "Cafe Aramesh API"
    environment: str = "development"
    debug: bool = True
    database_url: str = "postgresql+psycopg://cafe:cafe@localhost:5432/cafe_aramesh"
    waiter_pin: str = ""
    confirmation_ttl_minutes: int = 15


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
