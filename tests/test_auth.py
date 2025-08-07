import pytest
from fastapi import status

class TestUserRegistration:
    
    def test_register_user_success(self, client):
        user_data = {
            "email": "newuser@example.com",
            "username": "newuser",
            "password": "NewPassword123",
            "full_name": "New User"
        }
        response = client.post("/auth/register", json=user_data)
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["email"] == user_data["email"]
        assert data["username"] == user_data["username"]
        assert data["full_name"] == user_data["full_name"]
        assert data["is_active"]
        assert not data["is_admin"]
        assert "id" in data
        assert "created_at" in data

    def test_register_user_duplicate_email(self, client, test_user):
        user_data = {
            "email": "test@example.com",
            "username": "differentuser",
            "password": "Password123",
            "full_name": "Different User"
        }
        response = client.post("/auth/register", json=user_data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "Email already registered" in response.json()["detail"]

    def test_register_user_duplicate_username(self, client, test_user):
        user_data = {
            "email": "different@example.com",
            "username": "testuser",
            "password": "Password123",
            "full_name": "Different User"
        }
        response = client.post("/auth/register", json=user_data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "Username already registered" in response.json()["detail"]

    def test_register_user_invalid_email(self, client):
        user_data = {
            "email": "invalid-email",
            "username": "testuser2",
            "password": "Password123",
        }
        response = client.post("/auth/register", json=user_data)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_register_user_weak_password(self, client):
        user_data = {
            "email": "test2@example.com",
            "username": "testuser2",
            "password": "weak",
        }
        response = client.post("/auth/register", json=user_data)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_register_user_invalid_username(self, client):
        user_data = {
            "email": "test2@example.com",
            "username": "ab",
            "password": "Password123",
        }
        response = client.post("/auth/register", json=user_data)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


class TestUserLogin:
    
    def test_login_success_with_username(self, client, test_user):
        login_data = {
            "username": "testuser",
            "password": "TestPassword123"
        }
        response = client.post("/auth/login", json=login_data)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"
        assert data["expires_in"] == 3600

    def test_login_success_with_email(self, client, test_user):
        login_data = {
            "username": "test@example.com",
            "password": "TestPassword123"
        }
        response = client.post("/auth/login", json=login_data)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data

    def test_login_invalid_username(self, client):
        login_data = {
            "username": "nonexistent",
            "password": "Password123"
        }
        response = client.post("/auth/login", json=login_data)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert "Incorrect username or password" in response.json()["detail"]

    def test_login_invalid_password(self, client, test_user):
        login_data = {
            "username": "testuser",
            "password": "WrongPassword123"
        }
        response = client.post("/auth/login", json=login_data)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert "Incorrect username or password" in response.json()["detail"]

    def test_login_inactive_user(self, client, db_session):
        from app.models import User
        from app.auth import get_password_hash
        inactive_user = User(
            email="inactive@example.com",
            username="inactive",
            hashed_password=get_password_hash("Password123"),
            is_active=False
        )
        db_session.add(inactive_user)
        db_session.commit()
        login_data = {
            "username": "inactive",
            "password": "Password123"
        }
        response = client.post("/auth/login", json=login_data)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestTokenRefresh:
    
    def test_refresh_token_success(self, client, test_user):
        login_response = client.post("/auth/login", json={
            "username": "testuser",
            "password": "TestPassword123"
        })
        refresh_token = login_response.json()["refresh_token"]
        response = client.post("/auth/refresh", json={
            "refresh_token": refresh_token
        })
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"

    def test_refresh_token_invalid(self, client):
        response = client.post("/auth/refresh", json={
            "refresh_token": "invalid_token"
        })
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert "Invalid refresh token" in response.json()["detail"]

    def test_refresh_token_reuse_prevention(self, client, test_user):
        login_response = client.post("/auth/login", json={
            "username": "testuser",
            "password": "TestPassword123"
        })
        refresh_token = login_response.json()["refresh_token"]
        first_refresh = client.post("/auth/refresh", json={
            "refresh_token": refresh_token
        })
        assert first_refresh.status_code == status.HTTP_200_OK
        second_refresh = client.post("/auth/refresh", json={
            "refresh_token": refresh_token
        })
        assert second_refresh.status_code == status.HTTP_401_UNAUTHORIZED
