from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    database_url: str = "postgresql://postgres:postgres@localhost:5432/medusa-store"
    redis_url: str = "redis://localhost:6379/1"
    medusa_backend_url: str = "http://localhost:9000"
    environment: str = "development"
    
    # Database schema
    db_schema: str = "recommendation"
    
    # Recommendation settings
    max_recommendations: int = 12
    cache_ttl_seconds: int = 3600  # 1 hour
    min_interactions_for_collaborative: int = 5
    
    # Algorithm weights
    content_weight: float = 0.4
    collaborative_weight: float = 0.6
    
    class Config:
        env_file = ".env"

@lru_cache()
def get_settings():
    return Settings()
