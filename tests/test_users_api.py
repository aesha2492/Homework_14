"""
Basic user API tests for backward compatibility with Module 11.
For comprehensive endpoint tests, see tests/integration/test_users_calculations_api.py
"""
import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.database import get_db


@pytest.fixture
def client(override_get_db):
    """Create a test client with database override"""
    app.dependency_overrides[get_db] = lambda: override_get_db
    return TestClient(app)


def test_create_user_success(client):
    """Test successful user creation via POST /users/"""
    response = client.post(
        "/users/",
        json={
            "username": "testuser",
            "email": "test@example.com",
            "password": "testpassword123",
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["username"] == "testuser"
    assert data["email"] == "test@example.com"
    assert "id" in data
    assert "created_at" in data


def test_create_user_duplicate_email(client):
    """Test that duplicate emails are rejected"""
    # First user
    client.post(
        "/users/",
        json={
            "username": "user1",
            "email": "dup@example.com",
            "password": "password123",
        },
    )
    # Second user with same email
    response = client.post(
        "/users/",
        json={
            "username": "user2",
            "email": "dup@example.com",
            "password": "password456",
        },
    )
    assert response.status_code == 400
    assert "already exists" in response.json()["detail"]
