#Define the BASE_URL for your running server.
#Test the /health endpoint to make sure the API is alive.
#Test user registration (using a random username to keep it unique).
#Test logging in with that new user.
#Test the protected /users/me endpoint using the token from the login.
import pytest
import httpx
import random
import string

# The base URL for our running API
BASE_URL = "http://localhost:8000"

# Generate a random username for each test run
def random_username():
    return "".join(random.choices(string.ascii_lowercase, k=10))

@pytest.mark.order(1)
def test_health_check():
    """Test if the /health endpoint is working."""
    with httpx.Client(base_url=BASE_URL) as client:
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"
        assert response.json()["database"] == "connected"

@pytest.mark.run(order=2)
def test_register_user():
    """Test registering a new user."""
    global test_user, test_password
    test_user = random_username()
    test_password = "testpassword123"
    
    with httpx.Client(base_url=BASE_URL) as client:
        response = client.post(
            "/users/register",
            json={"username": test_user, "password": test_password}
        )
        assert response.status_code == 201
        data = response.json()
        assert data["username"] == test_user
        assert "id" in data

@pytest.mark.run(order=3)
def test_login_for_access_token():
    """Test logging in with the newly registered user."""
    global access_token
    
    form_data = {
        "username": test_user,
        "password": test_password
    }
    
    with httpx.Client(base_url=BASE_URL) as client:
        response = client.post("/token", data=form_data)
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        
        # Save the token for the next test
        access_token = data["access_token"]

@pytest.mark.run(order=4)
def test_read_users_me():
    """Test the protected /users/me endpoint."""
    
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    
    with httpx.Client(base_url=BASE_URL, headers=headers) as client:
        response = client.get("/users/me")
        assert response.status_code == 200
        data = response.json()
        assert data["username"] == test_user