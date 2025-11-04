"""练习 API 测试."""
import pytest
import httpx

from .test_category_question import register_and_login

pytestmark = pytest.mark.anyio(mode="asyncio")


async def _create_question(
    client: httpx.AsyncClient,
    headers: dict,
    question: str,
    answer: str = "A",
) -> int:
    response = await client.post(
        "/api/v1/question/",
        json={
            "question": question,
            "question_type": "single_choice",
            "options": ["A. 选项一", "B. 选项二"],
            "answer": answer,
            "explanation": "解析",
        },
        headers=headers,
    )
    assert response.status_code == 201, response.text
    return response.json()["id"]


async def test_practice_flow_sequential(client: httpx.AsyncClient):
    headers = await register_and_login(client, "practice_user")
    first = await _create_question(client, headers, "题目一", answer="A")
    second = await _create_question(client, headers, "题目二", answer="B")

    preview_resp = await client.post(
        "/api/v1/practice/preview",
        json={
            "mode": "sequential",
            "question_types": ["single_choice"],
        },
        headers=headers,
    )
    assert preview_resp.status_code == 200
    preview = preview_resp.json()
    assert preview["total_count"] >= 2

    start_resp = await client.post(
        "/api/v1/practice/start",
        json={
            "mode": "sequential",
            "question_types": ["single_choice"],
            "question_ids": [second, first],
        },
        headers=headers,
    )
    assert start_resp.status_code == 200, start_resp.text
    payload = start_resp.json()
    assert payload["total_count"] == 2
    assert [item["id"] for item in payload["questions"]] == [second, first]
    session_id = payload["session_id"]

    answer_resp = await client.post(
        f"/api/v1/practice/{session_id}/answer",
        json={"question_id": first, "user_answer": "A"},
        headers=headers,
    )
    assert answer_resp.status_code == 200
    data = answer_resp.json()
    assert data["is_correct"] is True

    wrong_resp = await client.post(
        f"/api/v1/practice/{session_id}/answer",
        json={"question_id": second, "user_answer": "A"},
        headers=headers,
    )
    assert wrong_resp.status_code == 200
    assert wrong_resp.json()["is_correct"] is False

    finish_resp = await client.post(
        f"/api/v1/practice/{session_id}/finish", headers=headers
    )
    assert finish_resp.status_code == 200
    summary = finish_resp.json()
    assert summary["correct_count"] == 1
    assert summary["total_count"] == 2
    assert summary["correct_rate"] == 0.5

    detail_first = await client.get(f"/api/v1/question/{first}", headers=headers)
    detail_second = await client.get(f"/api/v1/question/{second}", headers=headers)
    assert detail_first.json()["practice_count"] == 1
    assert detail_first.json()["correct_count"] == 1
    assert detail_second.json()["practice_count"] == 1
    assert detail_second.json()["correct_count"] == 0


async def test_practice_question_not_in_session(client: httpx.AsyncClient):
    headers = await register_and_login(client, "practice_invalid")
    target = await _create_question(client, headers, "题目三", answer="A")
    await _create_question(client, headers, "题目四", answer="B")

    start_resp = await client.post(
        "/api/v1/practice/start",
        json={"mode": "sequential", "question_types": ["single_choice"]},
        headers=headers,
    )
    assert start_resp.status_code == 200
    session_id = start_resp.json()["session_id"]

    new_question = await _create_question(client, headers, "题目五", answer="C")

    invalid_resp = await client.post(
        f"/api/v1/practice/{session_id}/answer",
        json={"question_id": new_question, "user_answer": "C"},
        headers=headers,
    )
    assert invalid_resp.status_code == 400

    # 仍可以回答会话中的题目
    valid_resp = await client.post(
        f"/api/v1/practice/{session_id}/answer",
        json={"question_id": target, "user_answer": "A"},
        headers=headers,
    )
    assert valid_resp.status_code == 200


async def test_practice_start_without_questions(client: httpx.AsyncClient):
    headers = await register_and_login(client, "practice_empty")
    resp = await client.post(
        "/api/v1/practice/start",
        json={"mode": "sequential", "question_types": ["true_false"]},
        headers=headers,
    )
    assert resp.status_code == 400


async def test_practice_result_endpoint(client: httpx.AsyncClient):
    headers = await register_and_login(client, "practice_result")
    first = await _create_question(client, headers, "题目一", answer="A")
    second = await _create_question(client, headers, "题目二", answer="B")

    start_resp = await client.post(
        "/api/v1/practice/start",
        json={"mode": "sequential", "question_types": ["single_choice"]},
        headers=headers,
    )
    assert start_resp.status_code == 200
    start_payload = start_resp.json()
    session_id = start_payload["session_id"]
    ordered_ids = [item["id"] for item in start_payload["questions"]]
    assert ordered_ids == [first, second]

    await client.post(
        f"/api/v1/practice/{session_id}/answer",
        json={"question_id": first, "user_answer": "A"},
        headers=headers,
    )
    await client.post(
        f"/api/v1/practice/{session_id}/answer",
        json={"question_id": second, "user_answer": "A"},
        headers=headers,
    )

    finish_resp = await client.post(
        f"/api/v1/practice/{session_id}/finish", headers=headers
    )
    assert finish_resp.status_code == 200

    result_resp = await client.get(
        f"/api/v1/practice/{session_id}/result", headers=headers
    )
    assert result_resp.status_code == 200
    result = result_resp.json()
    assert result["session_id"] == session_id
    assert result["correct_count"] == 1
    assert result["total_count"] == 2
    assert result["correct_rate"] == 0.5
    assert len(result["answers"]) == 2
    assert result["answers"][0]["question_id"] == first
    assert result["answers"][1]["question_id"] == second
    assert len(result["answers"][0]["options"]) == 2
    assert result["answers"][1]["is_correct"] is False


async def test_practice_history_list(client: httpx.AsyncClient):
    headers = await register_and_login(client, "practice_history")
    await _create_question(client, headers, "题目", answer="A")

    async def _run_session(mode: str):
        start_resp = await client.post(
            "/api/v1/practice/start",
            json={"mode": mode, "question_types": ["single_choice"]},
            headers=headers,
        )
        assert start_resp.status_code == 200
        payload = start_resp.json()
        session_id = payload["session_id"]
        first_question = payload["questions"][0]["id"]
        await client.post(
            f"/api/v1/practice/{session_id}/answer",
            json={"question_id": first_question, "user_answer": "A"},
            headers=headers,
        )
        finish_resp = await client.post(
            f"/api/v1/practice/{session_id}/finish", headers=headers
        )
        assert finish_resp.status_code == 200
        return session_id

    await _run_session("sequential")
    await _run_session("sequential")
    await _run_session("random")

    history_resp = await client.get(
        "/api/v1/practice/history?page=1&page_size=2", headers=headers
    )
    assert history_resp.status_code == 200
    history = history_resp.json()
    assert history["total"] >= 3
    assert history["page"] == 1
    assert history["page_size"] == 2
    assert len(history["items"]) == 2
    assert history["items"][0]["mode"] == "random"
    first_start = history["items"][0]["start_time"]
    second_start = history["items"][1]["start_time"]
    assert first_start >= second_start
    assert history["items"][0]["correct_rate"] == 1.0

    filtered_resp = await client.get(
        "/api/v1/practice/history?page=1&page_size=10&mode=random",
        headers=headers,
    )
    assert filtered_resp.status_code == 200
    filtered = filtered_resp.json()
    assert filtered["total"] == 1
    assert len(filtered["items"]) == 1
    assert all(item["mode"] == "random" for item in filtered["items"])
