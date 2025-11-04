"""用户设置与个人信息接口测试。"""
import httpx
import pytest

from .test_category_question import register_and_login

pytestmark = pytest.mark.anyio(mode="asyncio")


async def _get_headers(client: httpx.AsyncClient, identifier: str = "settings_user") -> dict:
    return await register_and_login(client, identifier)


async def test_get_default_user_settings(client: httpx.AsyncClient):
    headers = await _get_headers(client)

    response = await client.get("/api/v1/user/settings", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["practice_mode"] == "random"
    assert data["answer_display_mode"] == "immediate"
    assert data["ai_provider"] == "openai"
    assert data["ai_model"] == "gpt-3.5-turbo"
    assert data["has_api_key"] is False


async def test_update_user_preferences(client: httpx.AsyncClient):
    headers = await _get_headers(client, "settings_pref")

    payload = {
        "practice_mode": "sequential",
        "answer_display_mode": "summary",
    }
    response = await client.put("/api/v1/user/settings", json=payload, headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["practice_mode"] == "sequential"
    assert data["answer_display_mode"] == "summary"
    assert data["has_api_key"] is False


async def test_update_ai_settings_and_clear_key(client: httpx.AsyncClient):
    headers = await _get_headers(client, "settings_ai")

    update_payload = {
        "ai_provider": "azure",
        "ai_model": "gpt-4.1",
        "api_key": "sk-test-key",
    }
    response = await client.put(
        "/api/v1/user/settings/ai", json=update_payload, headers=headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["ai_provider"] == "azure"
    assert data["ai_model"] == "gpt-4.1"
    assert data["has_api_key"] is True

    clear_payload = {"api_key": ""}
    clear_resp = await client.put(
        "/api/v1/user/settings/ai", json=clear_payload, headers=headers
    )
    assert clear_resp.status_code == 200
    clear_data = clear_resp.json()
    assert clear_data["has_api_key"] is False
    assert clear_data["ai_provider"] == "azure"


async def test_update_user_profile(client: httpx.AsyncClient):
    headers = await _get_headers(client, "settings_profile")

    payload = {"nickname": "新昵称", "avatar_url": "https://example.com/avatar.png"}
    response = await client.put("/api/v1/user/profile", json=payload, headers=headers)
    assert response.status_code == 200
    profile = response.json()
    assert profile["nickname"] == "新昵称"
    assert profile["avatar_url"] == "https://example.com/avatar.png"


async def test_change_password_success(client: httpx.AsyncClient):
    headers = await _get_headers(client, "settings_password")

    change_payload = {
        "old_password": "Password123!",
        "new_password": "Password456!",
    }
    response = await client.put(
        "/api/v1/user/password", json=change_payload, headers=headers
    )
    assert response.status_code == 200
    assert response.json()["message"] == "密码修改成功"

    # 新密码登录成功
    login_resp = await client.post(
        "/api/v1/auth/login",
        data={"username": "settings_password", "password": "Password456!"},
    )
    assert login_resp.status_code == 200

    # 旧密码登录失败
    old_resp = await client.post(
        "/api/v1/auth/login",
        data={"username": "settings_password", "password": "Password123!"},
    )
    assert old_resp.status_code == 401


async def test_change_password_invalid_old_password(client: httpx.AsyncClient):
    headers = await _get_headers(client, "settings_invalid_password")

    payload = {
        "old_password": "WrongPassword",
        "new_password": "Password999!",
    }
    response = await client.put(
        "/api/v1/user/password", json=payload, headers=headers
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "原密码不正确"


async def test_list_models_with_provided_key(monkeypatch, client: httpx.AsyncClient):
    headers = await _get_headers(client, "settings_list_models")

    monkeypatch.setattr(
        "app.services.ai_extractor.list_provider_models",
        lambda provider, api_key: ["model-a", "model-b"],
    )

    response = await client.post(
        "/api/v1/user/settings/models",
        json={"provider": "openai", "api_key": "sk-temp"},
        headers=headers,
    )
    assert response.status_code == 200
    assert response.json()["models"] == ["model-a", "model-b"]


async def test_list_models_uses_saved_key(monkeypatch, client: httpx.AsyncClient):
    headers = await _get_headers(client, "settings_list_saved")

    await client.put(
        "/api/v1/user/settings/ai",
        json={"ai_provider": "openai", "ai_model": "gpt-4o", "api_key": "sk-saved"},
        headers=headers,
    )

    calls = {"count": 0}

    def fake_list(provider, key):
        calls["count"] += 1
        assert key == "sk-saved"
        return ["gpt-4o"]

    monkeypatch.setattr("app.services.ai_extractor.list_provider_models", fake_list)

    response = await client.post(
        "/api/v1/user/settings/models",
        json={"provider": "openai"},
        headers=headers,
    )
    assert response.status_code == 200
    assert response.json()["models"] == ["gpt-4o"]
    assert calls["count"] == 1


async def test_list_models_without_key_returns_error(client: httpx.AsyncClient):
    headers = await _get_headers(client, "settings_list_missing")

    response = await client.post(
        "/api/v1/user/settings/models",
        json={"provider": "openai"},
        headers=headers,
    )
    assert response.status_code == 400
    assert "API Key" in response.json()["detail"]
