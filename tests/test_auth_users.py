from fastapi.testclient import TestClient

from tests.conftest import register, token


def test_first_user_is_admin_and_second_is_user(client: TestClient):
    admin = register(client, "admin", "admin@example.com")
    user = register(client, "user", "user@example.com")
    assert admin["role"] == "ADMIN"
    assert user["role"] == "USER"


def test_login_and_invalid_password(client: TestClient):
    register(client, "anna", "anna@example.com")
    assert client.post("/api/auth/login", json={"username": "anna", "password": "strong-pass-123"}).status_code == 200
    assert client.post("/api/auth/login", json={"username": "anna", "password": "wrong-password"}).status_code == 401


def test_profile_edit_and_public_profile(client: TestClient):
    register(client, "anna", "anna@example.com")
    headers = token(client, "anna")
    assert client.patch("/api/users/me", json={"first_name": "Anna"}, headers=headers).json()["first_name"] == "Anna"
    response = client.get("/api/users/anna")
    assert response.status_code == 200
    assert response.json()["photo_count"] == 0
    assert "email" not in response.json()


def test_admin_can_ban_user_and_banned_user_cannot_login_or_use_token(client: TestClient):
    register(client, "admin", "admin@example.com")
    register(client, "bob", "bob@example.com")
    bob_headers = token(client, "bob")
    response = client.patch("/api/users/bob/active", json={"is_active": False}, headers=token(client, "admin"))
    assert response.status_code == 200
    assert client.post("/api/auth/login", json={"username": "bob", "password": "strong-pass-123"}).status_code == 403
    assert client.get("/api/users/me", headers=bob_headers).status_code == 403


def test_regular_user_cannot_ban(client: TestClient):
    register(client, "admin", "admin@example.com")
    register(client, "bob", "bob@example.com")
    assert client.patch("/api/users/admin/active", json={"is_active": False}, headers=token(client, "bob")).status_code == 403


def test_admin_cannot_ban_self_or_last_admin_and_can_change_user_role(client: TestClient):
    register(client, "admin", "admin@example.com")
    register(client, "bob", "bob@example.com")
    headers = token(client, "admin")
    assert client.patch("/api/users/admin/active", json={"is_active": False}, headers=headers).status_code == 400
    changed = client.patch("/api/users/bob/role", json={"role": "MODERATOR"}, headers=headers)
    assert changed.status_code == 200
    assert changed.json()["role"] == "MODERATOR"
    assert client.patch("/api/users/bob/role", json={"role": "ADMIN"}, headers=headers).status_code == 422


def test_admin_can_delete_another_user_but_not_self(client: TestClient):
    register(client, "admin", "admin@example.com")
    register(client, "bob", "bob@example.com")
    headers = token(client, "admin")
    assert client.get("/api/users/me", headers=headers).json()["username"] == "admin"
    assert client.delete("/api/users/admin", headers=headers).status_code == 400
    assert client.delete("/api/users/bob", headers=headers).status_code == 204
    assert client.get("/api/users/bob").status_code == 404


def test_health_endpoint(client: TestClient):
    assert client.get("/health").json() == {"status": "ok"}
