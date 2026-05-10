from functools import lru_cache
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # App
    APP_NAME: str = "NexusAI"
    DEBUG: bool = False

    # Database
    DATABASE_URL: str = "postgresql+asyncpg://nexus:nexus123@postgres:5432/nexusai"

    # Redis
    REDIS_URL: str = "redis://redis:6379"

    # Ollama — lightweight models that run on CPU-only machines
    OLLAMA_BASE_URL: str = "http://ollama:11434"
    CHAT_MODEL: str = "llama3.2:3b"      # ~2 GB RAM
    EMBED_MODEL: str = "nomic-embed-text"  # ~274 MB

    # JWT
    SECRET_KEY: str = "change-this-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440  # 24 hours

    # Rate limiting
    RATE_LIMIT_REQUESTS: int = 10
    RATE_LIMIT_WINDOW: int = 60  # seconds

    # LangSmith
    LANGCHAIN_API_KEY: str = ""
    LANGCHAIN_TRACING_V2: bool = False
    LANGCHAIN_PROJECT: str = "nexusai"

    model_config = {"env_file": ".env", "extra": "ignore"}


@lru_cache()
def get_settings() -> Settings:
    return Settings()
