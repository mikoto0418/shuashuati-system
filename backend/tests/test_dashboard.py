from __future__ import annotations

import pytest

pytestmark = pytest.mark.anyio(mode="asyncio")


def _register_payload(identifier: str) -> dict[str, str]:
    return {
        "username": identifier,
        "email": f"{identifier}@example.com",
        "password": "Password123!",
        "nickname": "测试用户",
    }


async def _register_and_login(client, identifier: str = "user") -> dict[str, str]:
    await client.post("/api/v1/auth/register", json=_register_payload(identifier))
    login_resp = await client.post(
        "/api/v1/auth/login",
        data={"username": identifier, "password": "Password123!"},
    )
    token = login_resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


async def _create_question(client, headers, *, question: str, answer: str) -> int:
    resp = await client.post(
        "/api/v1/question/",
        json={
            "question": question,
            "question_type": "short_answer",
            "answer": answer,
        },
        headers=headers,
    )
    assert resp.status_code == 201
    return resp.json()["id"]


async def _start_and_answer(
    client,
    headers,
    question_id: int,
    answer: str,
) -> None:
    start_resp = await client.post(
        "/api/v1/practice/start",
        json={
            "mode": "sequential",
            "category_ids": [],
            "question_types": [],
            "question_ids": [question_id],
        },
        headers=headers,
    )
    assert start_resp.status_code == 200
    session = start_resp.json()
    payload = {
        "question_id": question_id,
        "user_answer": answer,
    }
    submit_resp = await client.post(
        f"/api/v1/practice/{session['session_id']}/answer",
        json=payload,
        headers=headers,
    )
    assert submit_resp.status_code == 200


async def _create_ai_import_batch(client, headers) -> None:
    resp = await client.post(
        "/api/v1/file/upload/confirm",
        json={
            "file_path": "dummy.txt",
            "original_name": "dummy.txt",
            "mode": "ai",
            "used_ai": True,
            "questions": [
                {
                    "index": 1,
                    "question": "AI 解析题目",
                    "question_type": "short_answer",
                    "options": [],
                    "answer": "42",
                    "explanation": "",
                    "raw_text": "",
                }
            ],
        },
        headers=headers,
    )
    assert resp.status_code == 200


async def test_dashboard_overview_stats(client):
    headers = await _register_and_login(client, "dashboard_user")

    # 初始统计应全部为 0
    initial_resp = await client.get(
        "/api/v1/dashboard/overview", headers=headers
    )
    assert initial_resp.status_code == 200
    initial_data = initial_resp.json()
    assert initial_data == {
        "today_completed": 0,
        "today_accuracy": 0.0,
        "pending_wrong_questions": 0,
        "total_practice_questions": 0,
        "total_favorites": 0,
        "ai_parse_count": 0,
    }

    question_wrong = await _create_question(
        client, headers, question="1+1=?", answer="2"
    )
    question_correct = await _create_question(
        client, headers, question="2+2=?", answer="4"
    )

    # 收藏题目
    fav_resp = await client.post(
        "/api/v1/favorite/",
        json={"question_id": question_wrong},
        headers=headers,
    )
    assert fav_resp.status_code == 200

    # 错题一次、正确一次（使用不同题目，确保错题记录保留）
    await _start_and_answer(client, headers, question_wrong, answer="wrong")
    await _start_and_answer(client, headers, question_correct, answer="4")

    # 创建一条 AI 导入记录
    await _create_ai_import_batch(client, headers)

    stats_resp = await client.get("/api/v1/dashboard/overview", headers=headers)
    assert stats_resp.status_code == 200
    stats = stats_resp.json()

    assert stats["today_completed"] == 2
    assert stats["total_practice_questions"] == 2
    assert stats["pending_wrong_questions"] == 1
    assert stats["total_favorites"] == 1
    assert stats["ai_parse_count"] == 1
    assert stats["today_accuracy"] == pytest.approx(0.5)
