"""管理员上传目录清理接口测试。"""
from __future__ import annotations

import os
from datetime import datetime, timedelta

import pytest

from app.core.config import settings
from app.models.ai_task import AITask, AITaskStatus
from app.models.user import User
from .conftest import TestingSessionLocal


@pytest.mark.anyio
async def test_cleanup_uploads_removes_expired_files(
    client,
    tmp_path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """管理员可以删除过期文件，同时保留受保护文件。"""

    monkeypatch.setattr(settings, "UPLOAD_DIR", str(tmp_path), raising=False)

    upload_root = tmp_path
    upload_root.mkdir(parents=True, exist_ok=True)
    old_file = upload_root / "old.txt"
    old_file.write_text("old", encoding="utf-8")
    new_file = upload_root / "new.txt"
    new_file.write_text("new", encoding="utf-8")
    protected_file = upload_root / "protected.txt"
    protected_file.write_text("protected", encoding="utf-8")

    old_mtime = datetime.utcnow() - timedelta(hours=5)
    os.utime(old_file, (old_mtime.timestamp(), old_mtime.timestamp()))
    protected_mtime = datetime.utcnow() - timedelta(hours=5)
    os.utime(
        protected_file,
        (protected_mtime.timestamp(), protected_mtime.timestamp()),
    )

    admin_payload = {
        "username": "adminuser",
        "email": "admin@example.com",
        "password": "AdminPass123!",
        "nickname": "管理员",
    }
    register_response = await client.post(
        "/api/v1/auth/register",
        json=admin_payload,
    )
    assert register_response.status_code == 201

    login_response = await client.post(
        "/api/v1/auth/login",
        data={"username": admin_payload["username"], "password": admin_payload["password"]},
    )
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]

    with TestingSessionLocal() as db:
        admin = db.query(User).filter(User.email == admin_payload["email"]).first()
        assert admin is not None
        admin.is_admin = True
        task = AITask(
            user_id=admin.id,
            file_path=str(protected_file.resolve()),
            original_name="protected.txt",
            mode="mixed",
            status=AITaskStatus.RUNNING.value,
            progress=0.5,
        )
        db.add(task)
        db.commit()

    response = await client.post(
        "/api/v1/admin/uploads/cleanup",
        params={"retention_hours": 2},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    payload = response.json()
    assert "已清理" in payload["message"]

    assert not old_file.exists()
    assert new_file.exists()
    assert protected_file.exists()


@pytest.mark.anyio
async def test_cleanup_uploads_requires_admin(client) -> None:
    """非管理员访问应返回 403。"""
    user_payload = {
        "username": "normaluser",
        "email": "normal@example.com",
        "password": "Password123!",
        "nickname": "Regular User",
    }
    await client.post("/api/v1/auth/register", json=user_payload)
    with TestingSessionLocal() as db:
        user = db.query(User).filter(User.email == user_payload["email"]).first()
        assert user is not None
        user.is_admin = False
        db.commit()
    login_response = await client.post(
        "/api/v1/auth/login",
        data={"username": user_payload["username"], "password": user_payload["password"]},
    )
    token = login_response.json()["access_token"]

    response = await client.post(
        "/api/v1/admin/uploads/cleanup",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 403
    assert response.json()["detail"] == "需要管理员权限"
