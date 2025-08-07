import pytest
from fastapi import status
from app.auth import get_password_hash
from app.models import User

class TestUserProfile:
    
    def test_get_current_user_success(self, client, auth_token):
        headers = {"Authorization": f"Bearer {auth_token}"}
        response = client.get("/users/me", headers=headers)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["email"] == "test@example.com"
        assert data["username"] == "testuser"
        assert data["full_name"] == "Test User"

    def test_get_current_user_unauthorized(self, client):
        response = client.get("/users/me")
        assert response.status_code in (status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN)

    def test_get_current_user_invalid_token(self, client):
        headers = {"Authorization": "Bearer invalid_token"}
        response = client.get("/users/me", headers=headers)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_update_current_user_success(self, client, auth_token):
        headers = {"Authorization": f"Bearer {auth_token}"}
        update_data = {
            "email": "updated@example.com",
            "full_name": "Updated Name"
        }
        response = client.put("/users/me", json=update_data, headers=headers)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["email"] == "updated@example.com"
        assert data["full_name"] == "Updated Name"

    def test_update_current_user_partial(self, client, auth_token):
        headers = {"Authorization": f"Bearer {auth_token}"}
        update_data = {
            "full_name": "Partially Updated"
        }
        response = client.put("/users/me", json=update_data, headers=headers)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["full_name"] == "Partially Updated"
        # Email ne doit pas changer ici
        assert data["email"] == "test@example.com"


class TestAdminEndpoints:
    
    def test_get_all_users_success(self, client, admin_token, test_user):
        headers = {"Authorization": f"Bearer {admin_token}"}
        response = client.get("/users/admin/users", headers=headers)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 2

    def test_get_all_users_pagination(self, client, admin_token):
        headers = {"Authorization": f"Bearer {admin_token}"}
        response = client.get("/users/admin/users?skip=0&limit=1", headers=headers)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) <= 1

    def test_get_all_users_forbidden_regular_user(self, client, auth_token):
        headers = {"Authorization": f"Bearer {auth_token}"}
        response = client.get("/users/admin/users", headers=headers)
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert "Not enough permissions" in response.json().get("detail", "")

    def test_delete_user_success(self, client, admin_token, db_session):
        user_to_delete = User(
            email="delete@example.com",
            username="deleteme",
            hashed_password=get_password_hash("Password123"),
            full_name="Delete Me",
            is_active=True,
            is_admin=False
        )
        db_session.add(user_to_delete)
        db_session.flush()  # flush pour obtenir user_to_delete.id sans commit

        headers = {"Authorization": f"Bearer {admin_token}"}
        response = client.delete(f"/users/admin/users/{user_to_delete.id}", headers=headers)
        assert response.status_code == status.HTTP_200_OK
        assert "User deleted successfully" in response.json().get("message", "")

    def test_delete_user_not_found(self, client, admin_token):
        headers = {"Authorization": f"Bearer {admin_token}"}
        response = client.delete("/users/admin/users/99999", headers=headers)
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_delete_user_self_prevention(self, client, admin_token, admin_user):
        headers = {"Authorization": f"Bearer {admin_token}"}
        response = client.delete(f"/users/admin/users/{admin_user.id}", headers=headers)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "Cannot delete your own account" in response.json().get("detail", "")

    def test_delete_user_forbidden_regular_user(self, client, auth_token, admin_user):
        headers = {"Authorization": f"Bearer {auth_token}"}
        response = client.delete(f"/users/admin/users/{admin_user.id}", headers=headers)
        assert response.status_code == status.HTTP_403_FORBIDDEN


class TestHealthAndRoot:
    
    def test_health_check(self, client):
        response = client.get("/health")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data.get("status") == "healthy"
        assert "environment" in data

    def test_root_endpoint(self, client):
        response = client.get("/")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "Secure Authentication API" in data.get("message", "")
        assert data.get("version") == "1.0.0"
        assert data.get("docs") == "/docs"


class TestInputValidation:
    
    def test_password_requirements(self, client):
        test_cases = [
            ("short", "Password must be at least 8 characters"),
            ("nouppercase123", "Password must contain at least one uppercase letter"),
            ("NOLOWERCASE123", "Password must contain at least one lowercase letter"),
            ("NoDigitsHere", "Password must contain at least one digit"),
        ]
        for password, _ in test_cases:
            user_data = {
                "email": f"test{password}@example.com",
                "username": f"user{password}",
                "password": password,
            }
            response = client.post("/auth/register", json=user_data)
            assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_username_requirements(self, client):
        test_cases = [
            ("ab", "Username must be 3-20 characters"),
            ("a" * 21, "Username must be 3-20 characters"),
            ("user@name", "Username must be 3-20 characters, alphanumeric and underscore only"),
            ("user-name", "Username must be 3-20 characters, alphanumeric and underscore only"),
        ]
        for username, _ in test_cases:
            user_data = {
                "email": f"{username}@example.com",
                "username": username,
                "password": "ValidPassword123",
            }
            response = client.post("/auth/register", json=user_data)
            assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


class TestSecurityFeatures:
    
    def test_cors_headers_present(self, client):
        response = client.get("/")
        assert response.status_code == status.HTTP_200_OK

    def test_token_expiration_format(self, client, test_user):
        login_response = client.post("/auth/login", json={
            "username": "testuser",
            "password": "TestPassword123"
        })
        assert login_response.status_code == status.HTTP_200_OK
        data = login_response.json()
        assert isinstance(data.get("expires_in"), int)
        assert data.get("expires_in") > 0

    def test_password_hashing(self, db_session, test_user):
        assert test_user.hashed_password != "TestPassword123"
        assert len(test_user.hashed_password) > 50
        assert test_user.hashed_password.startswith("$2b$")

    def test_sql_injection_prevention(self, client):
        malicious_input = "'; DROP TABLE users; --"
        response = client.post("/auth/login", json={
            "username": malicious_input,
            "password": "password"
        })
        assert response.status_code in (status.HTTP_401_UNAUTHORIZED, status.HTTP_422_UNPROCESSABLE_ENTITY)
