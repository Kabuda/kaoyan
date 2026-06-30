from functools import lru_cache

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Kaoyan 11408 Study Dashboard"
    environment: str = "development"
    database_url: str = (
        "mysql+pymysql://kaoyan:kaoyan_password@localhost:3306/kaoyan?charset=utf8mb4"
    )
    jwt_secret: str = Field(default="change-this-secret-before-deploy", min_length=16)
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 24
    initial_admin_username: str = "admin"
    initial_admin_password: str = Field(default="change-me-now", min_length=8)
    cors_origins: list[str] = ["http://localhost:5173"]

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    @field_validator("cors_origins", mode="before")
    @classmethod
    def split_cors_origins(cls, value: str | list[str]) -> list[str]:
        if isinstance(value, str):
            return [item.strip() for item in value.split(",") if item.strip()]
        return value


@lru_cache
def get_settings() -> Settings:
    return Settings()

