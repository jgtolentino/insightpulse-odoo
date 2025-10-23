from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    # Superset
    superset_url: str = "http://localhost:8088"
    superset_username: str = "admin"
    superset_password: str = "admin"
    superset_provider: str = "db"
    dataset_id: int = 1

    # Odoo database
    odoo_db_url: str = "postgresql://odoo:password@postgres:5432/odoo"

    # OpenAI
    openai_api_key: str = ""
    openai_model: str = "gpt-4o-mini"

    # Redis
    redis_url: str = "redis://redis:6379/2"

    class Config:
        env_file = ".env"
        case_sensitive = False

@lru_cache()
def get_settings():
    return Settings()

settings = get_settings()
