"""Wrong question API tests."""
import httpx
import pytest

from .test_category_question import register_and_login

pytestmark = pytest.mark.anyio(mode="asyncio")


async def create_question(client: httpx.AsyncClient, headers: dict, text: str) -> int:
    response = await client.post(
        "/api/v1/question/",
        json={
            "question": text,
            "question_type": "single_choice",
            "options": ["A. 1", "B. 2"],
            "answer": "B",
            "category_id": None
        },
        headers=headers,
    )
    response.raise_for_status()
    return response.json()["id"]


async def start_and_answer_wrong(
    client: httpx.AsyncClient,
    headers: dict,
    question_id: int,
) -> None:
    start_resp = await client.post(
        "/api/v1/practice/start",
        json={"mode": "sequential", "question_types": ["single_choice"], "category_ids": []},
        headers=headers,
    )
    start_resp.raise_for_status()
    data = start_resp.json()
    session_id = data["session_id"]
    assert data["total_count"] >= 1

    await client.post(
        f"/api/v1/practice/{session_id}/answer",
        json={"question_id": question_id, "user_answer": "A"},
        headers=headers,
    )
    await client.post(f"/api/v1/practice/{session_id}/finish", headers=headers)


async def test_wrong_question_flow(client: httpx.AsyncClient):
    headers = await register_and_login(client, "wrong_user")
    question_id = await create_question(client, headers, "1 + 1 = ?")

    await start_and_answer_wrong(client, headers, question_id)

    list_resp = await client.get("/api/v1/wrong-question/", headers=headers)
    assert list_resp.status_code == 200
    items = list_resp.json()
    assert len(items) == 1
    assert items[0]["question_id"] == question_id

    delete_resp = await client.delete(
        f"/api/v1/wrong-question/{question_id}", headers=headers
    )
    assert delete_resp.status_code == 200
    assert delete_resp.json()["message"] == "Wrong question removed"

    after_resp = await client.get("/api/v1/wrong-question/", headers=headers)
    assert after_resp.status_code == 200
    assert after_resp.json() == []
