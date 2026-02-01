from pydantic_settings import BaseSettings
from pydantic import field_validator
from functools import lru_cache

class Settings(BaseSettings):
    app_name: str = "MorphoStruct API"
    debug: bool = False

    # LLM provider settings
    llm_provider: str = "anthropic"  # "anthropic" or "openai"
    anthropic_api_key: str = ""
    openai_api_key: str = ""
    openai_base_url: str = ""  # Custom OpenAI-compatible endpoint (e.g., Harvard proxy)
    llm_model: str = ""  # Optional: override default model for provider

    # Generation settings
    default_resolution: int = 16
    max_triangles: int = 500000
    generation_timeout_seconds: int = 60  # Timeout for scaffold generation (must be multiple of 30)

    @field_validator('generation_timeout_seconds')
    @classmethod
    def validate_timeout_multiple_of_30(cls, v: int) -> int:
        if v <= 0:
            raise ValueError('generation_timeout_seconds must be positive')
        if v % 30 != 0:
            raise ValueError('generation_timeout_seconds must be a multiple of 30 seconds')
        return v

    # Database settings
    database_url: str = "sqlite:///./morphostruct.db"

    # JWT Authentication settings
    jwt_secret_key: str = "morphostruct-dev-secret-key-change-in-production"
    access_token_expire_minutes: int = 1440

    # Encryption for API keys
    encryption_secret: str = "morphostruct-encryption-secret-change-in-production"

    class Config:
        env_file = ".env"

@lru_cache
def get_settings() -> Settings:
    return Settings()
