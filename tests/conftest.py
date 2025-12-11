import pytest
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base, get_db
from app.main import app

@pytest.fixture
def test_db(db_session):
    """
    Alias fixture so tests that expect `test_db` can reuse the existing `db_session` fixture.
    """
    return db_session

# Get DATABASE_URL from environment or use default
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./test_db.db")

# Create engine
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
)

# Create session factory
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db_session():
    """
    Create a fresh database for each test.
    
    Creates all tables, yields the session, then drops all tables.
    """
    # Create all tables
    Base.metadata.create_all(bind=engine)
    
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        # Drop all tables after test
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def override_get_db(db_session):
    """Override the get_db dependency for API tests"""
    def _override_get_db():
        return db_session
    
    app.dependency_overrides[get_db] = _override_get_db
    yield db_session
    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
def client(override_get_db):
    """Provide a test client with database override"""
    from fastapi.testclient import TestClient
    return TestClient(app)
