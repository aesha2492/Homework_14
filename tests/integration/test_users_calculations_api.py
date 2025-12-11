"""
Integration tests for user and calculation API endpoints.

Tests the full stack: FastAPI routes → CRUD functions → Database
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.main import app
from app.database import get_db


@pytest.fixture
def client(override_get_db):
    """Create a test client with overridden database dependency"""
    app.dependency_overrides[get_db] = lambda: override_get_db
    return TestClient(app)


# ============================================================================
# USER ENDPOINT TESTS
# ============================================================================

class TestUserEndpoints:
    """Tests for user registration, login, and retrieval endpoints"""

    def test_register_user_success(self, client, db_session: Session):
        """Test successful user registration via POST /users/register"""
        response = client.post(
            "/users/register",
            json={
                "username": "newuser",
                "email": "newuser@example.com",
                "password": "securepass123",
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert data["username"] == "newuser"
        assert data["email"] == "newuser@example.com"
        assert "id" in data
        assert "created_at" in data
        assert "password" not in data  # Ensure password is not returned

    def test_register_user_backward_compat_old_endpoint(self, client, db_session: Session):
        """Test that old /users/ endpoint still works (backward compatibility)"""
        response = client.post(
            "/users/",
            json={
                "username": "olduser",
                "email": "olduser@example.com",
                "password": "securepass123",
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert data["username"] == "olduser"

    def test_register_user_duplicate_username(self, client, db_session: Session):
        """Test registration fails with duplicate username"""
        # First user
        client.post(
            "/users/register",
            json={
                "username": "duplicate",
                "email": "first@example.com",
                "password": "pass123456",
            },
        )
        # Attempt duplicate
        response = client.post(
            "/users/register",
            json={
                "username": "duplicate",
                "email": "second@example.com",
                "password": "pass123456",
            },
        )
        assert response.status_code == 400
        assert "already exists" in response.json()["detail"]

    def test_register_user_duplicate_email(self, client, db_session: Session):
        """Test registration fails with duplicate email"""
        # First user
        client.post(
            "/users/register",
            json={
                "username": "user1",
                "email": "duplicate@example.com",
                "password": "pass123456",
            },
        )
        # Attempt duplicate email
        response = client.post(
            "/users/register",
            json={
                "username": "user2",
                "email": "duplicate@example.com",
                "password": "pass123456",
            },
        )
        assert response.status_code == 400
        assert "already exists" in response.json()["detail"]

    def test_register_user_invalid_email(self, client, db_session: Session):
        """Test registration fails with invalid email"""
        response = client.post(
            "/users/register",
            json={
                "username": "baduser",
                "email": "not-an-email",
                "password": "pass123456",
            },
        )
        assert response.status_code == 422  # Validation error

    def test_register_user_weak_password(self, client, db_session: Session):
        """Test registration fails with password < 8 characters"""
        response = client.post(
            "/users/register",
            json={
                "username": "weakpass",
                "email": "weak@example.com",
                "password": "short",  # Too short
            },
        )
        assert response.status_code == 422  # Validation error

    def test_login_user_success(self, client, db_session: Session):
        """Test successful login"""
        # Register user first
        client.post(
            "/users/register",
            json={
                "username": "loginuser",
                "email": "login@example.com",
                "password": "correctpass123",
            },
        )
        # Login
        response = client.post(
            "/users/login",
            json={
                "username": "loginuser",
                "password": "correctpass123",
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["username"] == "loginuser"
        assert data["email"] == "login@example.com"

    def test_login_user_wrong_password(self, client, db_session: Session):
        """Test login fails with wrong password"""
        # Register user
        client.post(
            "/users/register",
            json={
                "username": "wrongpass",
                "email": "wrong@example.com",
                "password": "correctpass123",
            },
        )
        # Login with wrong password
        response = client.post(
            "/users/login",
            json={
                "username": "wrongpass",
                "password": "wrongpassword",
            },
        )
        assert response.status_code == 401
        assert "Invalid username or password" in response.json()["detail"]

    def test_login_user_not_found(self, client, db_session: Session):
        """Test login fails for non-existent user"""
        response = client.post(
            "/users/login",
            json={
                "username": "nonexistent",
                "password": "anypassword",
            },
        )
        assert response.status_code == 401

    def test_read_user_success(self, client, db_session: Session):
        """Test retrieving user by ID"""
        # Register user
        register_response = client.post(
            "/users/register",
            json={
                "username": "readuser",
                "email": "read@example.com",
                "password": "readpass123",
            },
        )
        user_id = register_response.json()["id"]

        # Read user
        response = client.get(f"/users/{user_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == user_id
        assert data["username"] == "readuser"

    def test_read_user_not_found(self, client, db_session: Session):
        """Test reading non-existent user returns 404"""
        response = client.get("/users/99999")
        assert response.status_code == 404
        assert "User not found" in response.json()["detail"]


# ============================================================================
# CALCULATION ENDPOINT TESTS (BREAD)
# ============================================================================

class TestCalculationEndpoints:
    """Tests for calculation BREAD (Browse, Read, Edit, Add, Delete) endpoints"""

    def test_create_calculation_success(self, client, db_session: Session):
        """Test creating a calculation via POST /calculations/"""
        response = client.post(
            "/calculations/",
            json={
                "a": 10.0,
                "b": 5.0,
                "type": "Add",
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert data["a"] == 10.0
        assert data["b"] == 5.0
        assert data["type"] == "Add"
        assert data["result"] == 15.0  # Computed result
        assert "id" in data

    def test_create_calculation_subtract(self, client, db_session: Session):
        """Test creating a subtract calculation"""
        response = client.post(
            "/calculations/",
            json={
                "a": 20.0,
                "b": 8.0,
                "type": "Sub",
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert data["result"] == 12.0

    def test_create_calculation_multiply(self, client, db_session: Session):
        """Test creating a multiply calculation"""
        response = client.post(
            "/calculations/",
            json={
                "a": 7.0,
                "b": 6.0,
                "type": "Multiply",
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert data["result"] == 42.0

    def test_create_calculation_divide(self, client, db_session: Session):
        """Test creating a divide calculation"""
        response = client.post(
            "/calculations/",
            json={
                "a": 20.0,
                "b": 4.0,
                "type": "Divide",
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert data["result"] == 5.0

    def test_create_calculation_divide_by_zero(self, client, db_session: Session):
        """Test that divide by zero is rejected"""
        response = client.post(
            "/calculations/",
            json={
                "a": 10.0,
                "b": 0.0,
                "type": "Divide",
            },
        )
        assert response.status_code == 422  # Validation error

    def test_create_calculation_invalid_type(self, client, db_session: Session):
        """Test creation fails with invalid operation type"""
        response = client.post(
            "/calculations/",
            json={
                "a": 10.0,
                "b": 5.0,
                "type": "InvalidOp",
            },
        )
        assert response.status_code == 422

    def test_read_all_calculations_empty(self, client, db_session: Session):
        """Test reading all calculations when none exist"""
        response = client.get("/calculations/")
        assert response.status_code == 200
        data = response.json()
        assert data == []

    def test_read_all_calculations(self, client, db_session: Session):
        """Test reading all calculations"""
        # Create multiple calculations
        client.post("/calculations/", json={"a": 10, "b": 5, "type": "Add"})
        client.post("/calculations/", json={"a": 20, "b": 4, "type": "Divide"})

        response = client.get("/calculations/")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert data[0]["a"] == 10
        assert data[1]["a"] == 20

    def test_read_calculation_by_id(self, client, db_session: Session):
        """Test reading a specific calculation"""
        # Create calculation
        create_response = client.post(
            "/calculations/",
            json={"a": 100, "b": 25, "type": "Divide"},
        )
        calc_id = create_response.json()["id"]

        # Read specific calculation
        response = client.get(f"/calculations/{calc_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == calc_id
        assert data["a"] == 100
        assert data["b"] == 25
        assert data["result"] == 4.0

    def test_read_calculation_not_found(self, client, db_session: Session):
        """Test reading non-existent calculation returns 404"""
        response = client.get("/calculations/99999")
        assert response.status_code == 404
        assert "Calculation not found" in response.json()["detail"]

    def test_update_calculation_partial(self, client, db_session: Session):
        """Test updating a calculation with partial fields"""
        # Create calculation
        create_response = client.post(
            "/calculations/",
            json={"a": 10, "b": 5, "type": "Add"},
        )
        calc_id = create_response.json()["id"]

        # Update just the 'a' field
        response = client.put(
            f"/calculations/{calc_id}",
            json={"a": 30},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["a"] == 30
        assert data["b"] == 5  # Unchanged
        assert data["type"] == "Add"  # Unchanged
        assert data["result"] == 35.0  # Recalculated

    def test_update_calculation_type(self, client, db_session: Session):
        """Test updating the operation type"""
        # Create calculation
        create_response = client.post(
            "/calculations/",
            json={"a": 10, "b": 5, "type": "Add"},
        )
        calc_id = create_response.json()["id"]

        # Change type to Multiply
        response = client.put(
            f"/calculations/{calc_id}",
            json={"type": "Multiply"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["type"] == "Multiply"
        assert data["result"] == 50.0

    def test_update_calculation_not_found(self, client, db_session: Session):
        """Test updating non-existent calculation returns 404"""
        response = client.put(
            "/calculations/99999",
            json={"a": 100},
        )
        assert response.status_code == 404

    def test_delete_calculation_success(self, client, db_session: Session):
        """Test successful deletion of a calculation"""
        # Create calculation
        create_response = client.post(
            "/calculations/",
            json={"a": 10, "b": 5, "type": "Add"},
        )
        calc_id = create_response.json()["id"]

        # Delete it
        response = client.delete(f"/calculations/{calc_id}")
        assert response.status_code == 204

        # Verify it's gone
        response = client.get(f"/calculations/{calc_id}")
        assert response.status_code == 404

    def test_delete_calculation_not_found(self, client, db_session: Session):
        """Test deleting non-existent calculation returns 404"""
        response = client.delete("/calculations/99999")
        assert response.status_code == 404


# ============================================================================
# COMBINED / WORKFLOW TESTS
# ============================================================================

class TestIntegratedWorkflow:
    """Tests combining user and calculation operations"""

    def test_full_workflow_register_login_create_calculations(
        self, client, db_session: Session
    ):
        """Test full workflow: register → login → create calculations"""
        # Register user
        register_response = client.post(
            "/users/register",
            json={
                "username": "workflow",
                "email": "workflow@example.com",
                "password": "workflowpass123",
            },
        )
        assert register_response.status_code == 201
        user_id = register_response.json()["id"]

        # Login
        login_response = client.post(
            "/users/login",
            json={"username": "workflow", "password": "workflowpass123"},
        )
        assert login_response.status_code == 200

        # Create calculations
        calc1_response = client.post(
            "/calculations/",
            json={"a": 15, "b": 3, "type": "Multiply"},
        )
        assert calc1_response.status_code == 201

        calc2_response = client.post(
            "/calculations/",
            json={"a": 100, "b": 10, "type": "Divide"},
        )
        assert calc2_response.status_code == 201

        # Read all calculations
        all_calcs_response = client.get("/calculations/")
        assert all_calcs_response.status_code == 200
        assert len(all_calcs_response.json()) == 2

        # Read specific user
        user_response = client.get(f"/users/{user_id}")
        assert user_response.status_code == 200
        assert user_response.json()["username"] == "workflow"

    def test_multiple_users_multiple_calculations(
        self, client, db_session: Session
    ):
        """Test multiple users can each have calculations"""
        # User 1
        client.post(
            "/users/register",
            json={
                "username": "user1",
                "email": "user1@example.com",
                "password": "pass111111",
            },
        )

        # User 2
        client.post(
            "/users/register",
            json={
                "username": "user2",
                "email": "user2@example.com",
                "password": "pass222222",
            },
        )

        # Both users create calculations
        for i in range(3):
            client.post(
                "/calculations/",
                json={"a": i + 1, "b": i + 2, "type": "Add"},
            )

        # Verify all calculations are stored
        response = client.get("/calculations/")
        assert response.status_code == 200
        assert len(response.json()) == 3
