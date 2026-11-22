
from functools import lru_cache
from typing import Literal

from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Day 28 - Render Deployment API"
    app_env: Literal["development", "production"] = "development"

    database_url: str | None = None
    app_secret_key: str | None = None

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @model_validator(mode="after")
    def validate_production_settings(self) -> "Settings":
        if self.app_env == "production":
            if not self.database_url:
                raise ValueError(
                    "DATABASE_URL is required in production"
                )

            if not self.app_secret_key or len(self.app_secret_key) < 32:
                raise ValueError(
                    "APP_SECRET_KEY must contain at least 32 characters"
                )

        return self


@lru_cache
def get_settings() -> Settings:
    return Settings()
