from pydantic_settings import BaseSettings
# We don't need to import ConfigDict

class CelerySettings(BaseSettings):
    """Loads Celery-specific settings from .env."""
    
    # --- THIS IS THE FIX ---
    # model_config should be a plain dictionary,
    # not a ConfigDict() object.
    model_config = {
        "env_file": ".env",
        "extra": "ignore"
    }
    # --- END FIX ---

    CELERY_BROKER_URL: str = "redis://redis:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://redis:6379/0"


celery_settings = CelerySettings()