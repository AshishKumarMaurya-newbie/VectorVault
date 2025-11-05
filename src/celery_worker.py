import os
from celery import Celery
# --- FIX: Removed 'src.' prefix ---
from celery_config import celery_settings

# Create the Celery app instance
celery_app = Celery(
    "vectorvault_worker",
    broker=celery_settings.CELERY_BROKER_URL,
    backend=celery_settings.CELERY_RESULT_BACKEND,
    # --- FIX: Removed 'src.' prefix ---
    include=["tasks"]
)

celery_app.conf.update(
    task_track_started=True,
)