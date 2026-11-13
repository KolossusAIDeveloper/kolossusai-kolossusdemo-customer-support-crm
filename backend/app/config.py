from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    database_url: str = "postgresql://crmuser:crmpassword@localhost/crmdb"
    redis_url: str = "redis://localhost:6379/0"
    secret_key: str = "supersecretkey123changeme"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 24
    ai_provider: str = "openai"
    openai_api_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None

    class Config:
        env_file = ".env"


settings = Settings()
