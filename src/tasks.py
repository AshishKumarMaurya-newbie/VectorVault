import time
from celery_worker import celery_app

@celery_app.task(name="create_hello_world_task")
def create_hello_world_task(message: str):
    """
    A simple test task that simulates a long-running job.
    """
    print(f"Received job: {message}")
    
    # Simulate a slow process like processing a PDF
    time.sleep(10) 
    
    result = f"Task completed! You said: {message}"
    print(result)
    return result