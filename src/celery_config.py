from pydantic_settings import BaseSettings
from pydantic import ConfigDict  # <-- Import ConfigDict

class CelerySettings(BaseSettings):
    """Loads Celery-specific settings from .env."""
    
    # --- ADD THIS ---
    # This tells Pydantic to ignore any .env variables
    # that we haven't defined in this class.
    model_config = ConfigDict(extra='ignore')
    # --- END ADD ---

    CELERY_BROKER_URL: str = "redis://redis:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://redis:6379/0"

    class Config:
        env_file = ".env"

celery_settings = CelerySettings()