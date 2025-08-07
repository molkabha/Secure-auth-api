import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base, get_db
from app.main import app
from app.models import User
from app.auth import get_password_hash

TEST_DATABASE_URL = "postgresql://auth_user:auth_password@localhost:5432/test_auth_api_db"

engine = create_engine(TEST_DATABASE_URL)
TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
    bind=engine
)

@pytest.fixture(scope="session", autouse=True)
def setup_database():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def db_session():
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)
    yield session
    session.close()
    transaction.rollback()
    connection.close()

@pytest.fixture(scope="function")
def client(db_session):
    def _override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = _override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()

@pytest.fixture(scope="function")
def test_user(db_session):
    user = User(
        email="test@example.com",
        username="testuser",
        hashed_password=get_password_hash("TestPassword123"),
        full_name="Test User",
        is_active=True,
        is_admin=False
    )
    db_session.add(user)
    db_session.flush()  # flush mais pas commit !
    return user

@pytest.fixture(scope="function")
def admin_user(db_session):
    user = User(
        email="admin@example.com",
        username="admin",
        hashed_password=get_password_hash("AdminPassword123"),
        full_name="Admin User",
        is_active=True,
        is_admin=True
    )
    db_session.add(user)
    db_session.flush()  # flush mais pas commit !
    return user

@pytest.fixture(scope="function")
def auth_token(client, test_user):
    response = client.post("/auth/login", json={
        "username": "testuser",
        "password": "TestPassword123"
    })
    assert response.status_code == 200
    return response.json()["access_token"]

@pytest.fixture(scope="function")
def admin_token(client, admin_user):
    response = client.post("/auth/login", json={
        "username": "admin",
        "password": "AdminPassword123"
    })
    assert response.status_code == 200
    return response.json()["access_token"]
