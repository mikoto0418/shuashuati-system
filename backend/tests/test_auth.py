"""
用户认证接口测试
"""
import pytest
import httpx

pytestmark = pytest.mark.anyio(mode="asyncio")


def register_payload(username: str = "testuser", email: str = "test@example.com"):
    return {
        "username": username,
        "email": email,
        "password": "Password123!",
        "nickname": "测试用户"
    }


async def test_register_user_success(client: httpx.AsyncClient):
    response = await client.post("/api/v1/auth/register", json=register_payload())
    assert response.status_code == 201
    data = response.json()
    assert data["username"] == "testuser"
    assert data["email"] == "test@example.com"
    assert data["is_active"] is True


async def test_register_user_duplicate_username(client: httpx.AsyncClient):
    await client.post("/api/v1/auth/register", json=register_payload())
    response = await client.post("/api/v1/auth/register", json=register_payload(email="another@example.com"))
    assert response.status_code == 400
    assert response.json()["detail"] == "用户名已存在"


async def test_register_user_duplicate_email(client: httpx.AsyncClient):
    await client.post("/api/v1/auth/register", json=register_payload())
    dup_payload = register_payload(username="anotheruser")
    response = await client.post("/api/v1/auth/register", json=dup_payload)
    assert response.status_code == 400
    assert response.json()["detail"] == "邮箱已被注册"


async def test_login_success(client: httpx.AsyncClient):
    await client.post("/api/v1/auth/register", json=register_payload())
    response = await client.post(
        "/api/v1/auth/login",
        data={"username": "testuser", "password": "Password123!"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert data["user"]["username"] == "testuser"


async def test_login_with_email(client: httpx.AsyncClient):
    await client.post("/api/v1/auth/register", json=register_payload())
    response = await client.post(
        "/api/v1/auth/login",
        data={"username": "test@example.com", "password": "Password123!"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["user"]["email"] == "test@example.com"


async def test_login_invalid_credentials(client: httpx.AsyncClient):
    await client.post("/api/v1/auth/register", json=register_payload())
    response = await client.post(
        "/api/v1/auth/login",
        data={"username": "testuser", "password": "WrongPassword"}
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "用户名或密码错误"


async def test_get_current_user_requires_token(client: httpx.AsyncClient):
    response = await client.get("/api/v1/auth/me")
    assert response.status_code == 401


async def test_get_current_user_success(client: httpx.AsyncClient):
    await client.post("/api/v1/auth/register", json=register_payload())
    token_response = await client.post(
        "/api/v1/auth/login",
        data={"username": "testuser", "password": "Password123!"}
    )
    token = token_response.json()["access_token"]
    me_response = await client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert me_response.status_code == 200
    data = me_response.json()
    assert data["username"] == "testuser"
