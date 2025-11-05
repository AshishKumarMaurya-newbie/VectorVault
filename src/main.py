from fastapi import FastAPI, Depends, HTTPException, status, Form
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from sqlalchemy import text
from datetime import timedelta
import time
from contextlib import asynccontextmanager
import sqlalchemy.exc
from typing import Annotated

# --- NEW: Import for /metrics endpoint ---
from fastapi.responses import PlainTextResponse
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
# ---

# Import all your project modules
import crud, models, schemas, security
from database import engine, get_db, settings, SessionLocal
from monitoring import MetricsMiddleware, MetricsCollector, HealthCheck
from tasks import create_hello_world_task

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Run on app startup and shutdown.
    """
    print("--- THIS IS THE NEWEST VERSION ---")
    print("Application startup... Waiting for database...")
    
    retries = 10
    delay = 5
    db_ready = False

    for i in range(retries):
        try:
            db = SessionLocal()
            db.execute(text("SELECT 1"))
            db.close()
            db_ready = True
            print("✅ Database connected!")
            break
        except sqlalchemy.exc.OperationalError:
            print(f"Database not ready. Retrying in {delay}s... ({i+1}/{retries})")
            time.sleep(delay)

    if not db_ready:
        print("❌ Database connection failed after all retries. Shutting down.")
        raise Exception("Could not connect to database.")

    # We removed the create_all() line, Alembic handles this.
    
    yield
    
    print("Application shutdown...")


app = FastAPI(
    title="VectorVault API",
    description="A secure MLOps API for RAG pipelines.",
    version="0.1.0",
    lifespan=lifespan
)

# --- 1. Add Monitoring Middleware ---
app.add_middleware(MetricsMiddleware)


# --- 2. Authentication Endpoints ---

@app.post("/token", response_model=schemas.Token)
def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Session = Depends(get_db)
):
    """
    Standard OAuth2 login endpoint.
    """
    user = security.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = security.create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@app.post("/users/register", response_model=schemas.UserRead, status_code=status.HTTP_201_CREATED)
def register_new_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    """
    Register a new user in the database.
    """
    db_user = crud.get_user_by_username(db, username=user.username)
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
    return crud.create_user(db=db, user=user)


# --- 3. Protected Endpoint Example ---

@app.get("/users/me", response_model=schemas.UserRead)
def read_users_me(current_user: models.User = Depends(security.get_current_active_user)):
    """
    Example of a protected endpoint that requires a valid JWT token.
    """
    return current_user


# --- 4. Root and Health Endpoints ---

@app.get("/")
def root():
    return {"message": "Welcome to VectorVault API"}

@app.get("/health")
def health(db: Session = Depends(get_db)):
    """
    A realistic health check that also checks database connectivity.
    """
    try:
        db.execute(text("SELECT 1"))
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Database connection error: {e}"
        )


# --- 5. Asynchronous Task Endpoint ---

@app.post("/test-task")
def test_background_task():
    """
    Endpoint to trigger a new 10-second background task.
    """
    print("Received request to start test task...")
    create_hello_world_task.delay("Hello from the API!")
    print("Task was sent to the background worker. Returning response.")
    
    return {"message": "Task has been started in the background!"}


# --- 6. Prometheus Metrics Endpoint (NEW) ---

@app.get("/metrics", response_class=PlainTextResponse)
def metrics():
    """
    Prometheus metrics endpoint.
    """
    return generate_latest()