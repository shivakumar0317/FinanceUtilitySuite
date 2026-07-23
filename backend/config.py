from __future__ import annotations

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    app_name: str = "Finance Utility Suite"
    app_version: str = "1.8.1"
    environment: str = "development"
    debug: bool = True
    upload_dir: str = Field(default="uploads", alias="UPLOAD_DIR")

    database_url: str = Field(
        default="sqlite:///./finance_utility_suite.db",
        alias="DATABASE_URL",
    )
    jwt_secret_key: str = Field(
        default="change-this-secret-in-production",
        alias="JWT_SECRET_KEY",
    )
    jwt_algorithm: str = Field(default="HS256", alias="JWT_ALGORITHM")
    access_token_expire_minutes: int = Field(
        default=60,
        alias="ACCESS_TOKEN_EXPIRE_MINUTES",
    )
    cors_origins: str = Field(
        default="http://localhost:5173,http://localhost:5174",
        alias="CORS_ORIGINS",
    )

    @property
    def cors_origin_list(self) -> list[str]:
        return [
            origin.strip()
            for origin in self.cors_origins.split(",")
            if origin.strip()
        ]


@lru_cache
def get_settings() -> Settings:
    return Settings()
