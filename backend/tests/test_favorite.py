"""Favorite API tests."""
import httpx
import pytest

from .test_category_question import register_and_login

pytestmark = pytest.mark.anyio(mode="asyncio")


async def create_question(client: httpx.AsyncClient, headers: dict, index: int) -> int:
    response = await client.post(
        "/api/v1/question/",
        json={
            "question": f"Sample question {index}",
            "question_type": "single_choice",
            "options": ["A. opt1", "B. opt2"],
            "answer": "B",
            "category_id": None
        },
        headers=headers
    )
    response.raise_for_status()
    return response.json()["id"]


async def test_favorite_flow(client: httpx.AsyncClient):
    headers = await register_and_login(client, "favorite_user")
    question_id = await create_question(client, headers, 1)

    # add
    add_resp = await client.post(
        "/api/v1/favorite/",
        json={"question_id": question_id},
        headers=headers
    )
    assert add_resp.status_code == 200
    assert add_resp.json()["question_id"] == question_id

    # list
    list_resp = await client.get("/api/v1/favorite/", headers=headers)
    assert list_resp.status_code == 200
    favorites = list_resp.json()
    assert len(favorites) == 1
    assert favorites[0]["question_id"] == question_id

    # delete
    del_resp = await client.delete(
        f"/api/v1/favorite/{question_id}", headers=headers
    )
    assert del_resp.status_code == 200
    assert del_resp.json()["message"] == "Favorite removed"

    list_after = await client.get("/api/v1/favorite/", headers=headers)
    assert list_after.status_code == 200
    assert list_after.json() == []
