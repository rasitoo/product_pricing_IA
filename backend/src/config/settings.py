from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env.local", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "Resale Pricing Assistant"
    api_prefix: str = "/api/v1"
    database_url: str = "sqlite:///./app.db"
    redis_url: str = "redis://localhost:6379/0"
    openai_api_key: str = Field(default="")
    # Set LLM_STUB=true to skip real OpenAI calls (useful in tests and dev)
    llm_stub: bool = False
    image_storage_mode: str = "local"
    image_storage_path: str = "data/uploads"
    llm_daily_budget_usd: float = 25.0
    llm_request_timeout_seconds: int = 30


@lru_cache
def get_settings() -> Settings:
    return Settings()
