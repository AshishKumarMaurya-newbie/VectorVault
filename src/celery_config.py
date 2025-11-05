from pydantic_settings import BaseSettings

class CelerySettings(BaseSettings):
    """Loads Celery-specific settings from .env."""
    CELERY_BROKER_URL: str = "redis://redis:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://redis:6379/0"

    class Config:
        env_file = ".env"
        # If .env is not found, it will use the defaults above,
        # which are correct for our Docker setup.

celery_settings = CelerySettings()