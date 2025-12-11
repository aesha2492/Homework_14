import pytest
from pydantic import ValidationError
from app.schemas import UserCreate

def test_user_create_valid():
    user = UserCreate(
        username="tejen",
        email="tejen@example.com",
        password="strongpassword",
    )
    assert user.username == "tejen"

def test_user_create_invalid_email():
    with pytest.raises(ValidationError):
        UserCreate(
            username="testuser",
            email="not-an-email",
            password="strongpassword",
        )

def test_user_create_short_password():
    with pytest.raises(ValidationError):
        UserCreate(
            username="testuser",
            email="user@example.com",
            password="123",
        )
