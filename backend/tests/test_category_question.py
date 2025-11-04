"""
分类与题目 API 测试
"""
from pathlib import Path

import httpx
import pytest

pytestmark = pytest.mark.anyio(mode="asyncio")

_PNG_BYTES = (
    b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR"
    b"\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00"
    b"\x90wS\xde\x00\x00\x00\nIDATx\xdacd\xf8\x0f\x00\x01\x01\x01\x00"
    b"\x18\xdd\x8d\x1d\x00\x00\x00\x00IEND\xaeB`\x82"
)


def register_payload(username: str, email: str):
    return {
        "username": username,
        "email": email,
        "password": "Password123!",
        "nickname": "测试用户"
    }


async def register_and_login(client: httpx.AsyncClient, identifier: str = "user1") -> dict:
    await client.post("/api/v1/auth/register", json=register_payload(identifier, f"{identifier}@example.com"))
    response = await client.post(
        "/api/v1/auth/login",
        data={"username": identifier, "password": "Password123!"}
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


async def test_category_crud_flow(client: httpx.AsyncClient):
    headers = await register_and_login(client, "category_user")

    create_resp = await client.post(
        "/api/v1/category/",
        json={"name": "数学", "description": "基础数学"},
        headers=headers,
    )
    assert create_resp.status_code == 201
    category = create_resp.json()
    category_id = category["id"]

    list_resp = await client.get("/api/v1/category/", headers=headers)
    assert list_resp.status_code == 200
    assert len(list_resp.json()) == 1

    update_resp = await client.put(
        f"/api/v1/category/{category_id}",
        json={"description": "高等数学"},
        headers=headers,
    )
    assert update_resp.status_code == 200
    assert update_resp.json()["description"] == "高等数学"

    delete_resp = await client.delete(f"/api/v1/category/{category_id}", headers=headers)
    assert delete_resp.status_code == 200
    assert delete_resp.json()["message"] == "Category deleted"


async def test_question_flow(client: httpx.AsyncClient):
    headers = await register_and_login(client, "question_user")

    category_resp = await client.post(
        "/api/v1/category/",
        json={"name": "英语", "description": "语法"},
        headers=headers,
    )
    category_id = category_resp.json()["id"]

    create_question_resp = await client.post(
        "/api/v1/question/",
        json={
            "question": "What is 2 + 2?",
            "question_type": "single_choice",
            "options": ["A. 3", "B. 4"],
            "answer": "B",
            "explanation": "Basic addition",
            "tags": ["math"],
            "category_id": category_id
        },
        headers=headers,
    )
    assert create_question_resp.status_code == 201
    question_id = create_question_resp.json()["id"]

    list_resp = await client.get("/api/v1/question/", headers=headers)
    assert list_resp.status_code == 200
    data = list_resp.json()
    assert data["total"] == 1
    assert data["items"][0]["question"] == "What is 2 + 2?"

    detail_resp = await client.get(f"/api/v1/question/{question_id}", headers=headers)
    assert detail_resp.status_code == 200
    assert detail_resp.json()["answer"] == "B"

    update_resp = await client.put(
        f"/api/v1/question/{question_id}",
        json={"category_id": None, "tags": ["updated"]},
        headers=headers,
    )
    assert update_resp.status_code == 200
    assert update_resp.json()["category_id"] is None
    assert update_resp.json()["tags"] == ["updated"]

    delete_resp = await client.delete(f"/api/v1/question/{question_id}", headers=headers)
    assert delete_resp.status_code == 200

    # batch delete
    ids = []
    for idx in range(2):
        resp = await client.post(
            "/api/v1/question/",
            json={
                "question": f"Sample {idx}",
                "question_type": "short_answer",
                "answer": "OK",
                "category_id": None
            },
            headers=headers,
        )
        ids.append(resp.json()["id"])

    batch_resp = await client.request(
        "DELETE",
        "/api/v1/question/batch",
        json={"ids": ids},
        headers=headers,
    )
    assert batch_resp.status_code == 200, batch_resp.json()
    assert "Deleted" in batch_resp.json()["message"]

    final_list = await client.get("/api/v1/question/", headers=headers)
    assert final_list.json()["total"] == 0


async def test_question_image_upload(client: httpx.AsyncClient):
    headers = await register_and_login(client, "image_user")
    create_question_resp = await client.post(
        "/api/v1/question/",
        json={
            "question": "示例题目",
            "question_type": "short_answer",
            "answer": "答案",
        },
        headers=headers,
    )
    assert create_question_resp.status_code == 201
    question_id = create_question_resp.json()["id"]

    upload_resp = await client.post(
        "/api/v1/question/image",
        data={"question_id": str(question_id)},
        files={"upload_file": ("sample.png", _PNG_BYTES, "image/png")},
        headers=headers,
    )
    assert upload_resp.status_code == 200
    payload = upload_resp.json()
    assert payload["image_url"].startswith("/static/")
    assert payload["question_id"] == question_id

    relative_path = payload["relative_path"]
    saved_path = Path("static") / relative_path
    assert saved_path.exists()

    detail_resp = await client.get(f"/api/v1/question/{question_id}", headers=headers)
    assert detail_resp.status_code == 200
    assert detail_resp.json()["image_url"] == payload["image_url"]

    # 再次上传应生成新文件并清理旧文件
    upload_resp2 = await client.post(
        "/api/v1/question/image",
        data={"question_id": str(question_id)},
        files={"upload_file": ("sample2.png", _PNG_BYTES, "image/png")},
        headers=headers,
    )
    assert upload_resp2.status_code == 200
    payload2 = upload_resp2.json()
    assert payload2["relative_path"] != relative_path
    assert not saved_path.exists()

    # 设置 image_url 为 null 应删除现有图片
    update_resp = await client.put(
        f"/api/v1/question/{question_id}",
        json={"image_url": None},
        headers=headers,
    )
    assert update_resp.status_code == 200
    assert update_resp.json()["image_url"] is None
    new_saved_path = Path("static") / payload2["relative_path"]
    assert not new_saved_path.exists()

    # 非图片文件应返回 400
    invalid_resp = await client.post(
        "/api/v1/question/image",
        files={"upload_file": ("bad.txt", b"not-an-image", "text/plain")},
        headers=headers,
    )
    assert invalid_resp.status_code == 400
