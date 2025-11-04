"""文件上传预览测试。"""
import httpx
import pytest
from app.core.security import encrypt_api_key
from fastapi import HTTPException
from app.models.user import User, UserSettings
from app.services.ai_extractor import extract_questions_ai, _extract_json
from app.schemas.file import ParsedOptionSchema, ParsedQuestionSchema
from app.services.question_parser import ParsedOption as RuleParsedOption, ParsedQuestion as RuleParsedQuestion
from .test_category_question import register_and_login

pytestmark = pytest.mark.anyio(mode="asyncio")


async def _post_preview(
    client: httpx.AsyncClient,
    headers: dict[str, str],
    content: str,
    mode: str = "basic",
):
    files = {
        "upload_file": ("sample.txt", content.encode("utf-8"), "text/plain"),
        "mode": (None, mode),
    }
    return await client.post("/api/v1/file/upload/preview", headers=headers, files=files)


async def test_file_preview_basic_mode(client: httpx.AsyncClient):
    headers = await register_and_login(client, "file_basic")
    content = "1. 第一题\nA. 选项一\nB. 选项二\n答案：B"
    response = await _post_preview(client, headers, content, mode="basic")

    assert response.status_code == 200
    data = response.json()
    assert data["mode"] == "basic"
    assert data["used_ai"] is False
    assert len(data["questions"]) == 1
    assert data["questions"][0]["answer"] == "B"
    assert data["questions"][0]["tags"] == []


async def test_file_preview_ai_requires_key(client: httpx.AsyncClient):
    headers = await register_and_login(client, "file_ai_missing")
    content = "无题号的内容"
    response = await _post_preview(client, headers, content, mode="ai")

    assert response.status_code == 400
    assert "API Key" in response.json()["detail"]


async def test_file_preview_mixed_fallback_to_ai(monkeypatch, client: httpx.AsyncClient):
    headers = await register_and_login(client, "file_mixed")
    ai_result = [
        ParsedQuestionSchema(
            index=1,
            question="AI 生成题目",
            question_type="short_answer",
            options=[ParsedOptionSchema(key="A", content="解析结果")],
            answer="解析答案",
            explanation="",
            raw_text="",
            tags=["集合运算"],
        )
    ]

    monkeypatch.setattr(
        "app.api.v1.file.extract_questions_ai",
        lambda user, text: (
            ai_result,
            [],
            {
                "stats": {
                    "initial_segments": 1,
                    "processed_segments": 1,
                    "auto_split_segments": 0,
                    "provider": "mock",
                },
                "events": [],
            },
        ),
    )

    monkeypatch.setattr(
        "app.api.v1.file.parse_questions",
        lambda text: [
            RuleParsedQuestion(
                index=1,
                question="规则解析结果",
                question_type="single_choice",
                options=[
                    RuleParsedOption("A", "A. int show(...) | B. void show(...) | C. ...")
                ],
                answer="A",
                explanation="",
                raw_text="",
            )
        ],
    )

    response = await _post_preview(client, headers, "规则解析质量较差", mode="mixed")
    assert response.status_code == 200
    data = response.json()
    assert data["mode"] == "mixed"
    assert data["used_ai"] is True
    assert len(data["questions"]) == 1
    assert data["questions"][0]["question"] == "AI 生成题目"
    assert data["questions"][0]["tags"] == ["集合运算"]
    assert any("AI" in warning for warning in data["warnings"])


def test_extract_questions_ai_siliconflow(monkeypatch):
    user = User(
        id=1,
        username="demo",
        email="demo@example.com",
        hashed_password="hash",
    )
    user.settings = UserSettings(
        user_id=1,
        ai_provider="siliconflow",
        ai_model="silicon-model",
        encrypted_api_key=encrypt_api_key("sk-silicon"),
    )

    monkeypatch.setattr(
        "app.services.ai_extractor._call_siliconflow",
        lambda model, api_key, text: [
            {
                "index": 1,
                "question": "AI 题目",
                "question_type": "single_choice",
                "options": [{"key": "A", "content": "选项一"}],
                "answer": "A",
                "explanation": "",
                "tags": ["矩阵"],
            }
        ],
    )

    result, warnings, meta = extract_questions_ai(user, "内容")
    assert len(result) == 1
    assert result[0].question == "AI 题目"
    assert result[0].options[0].key == "A"
    assert result[0].tags == ["矩阵"]
    assert warnings == []
    assert meta["stats"]["processed_segments"] == 1
    assert meta["stats"]["tag_source"] == "ai"


def test_extract_questions_ai_chunking(monkeypatch):
    user = User(
        id=2,
        username="chunk",
        email="chunk@example.com",
        hashed_password="hash",
    )
    user.settings = UserSettings(
        user_id=2,
        ai_provider="openai",
        ai_model="gpt-test",
        encrypted_api_key=encrypt_api_key("sk-test"),
    )

    calls: list[str] = []

    def fake_openai(model: str, api_key: str, text: str):
        calls.append(text)
        return [
            {
                "index": 1,
                "question": f"Q{len(calls)}",
                "question_type": "short_answer",
                "answer": "A",
                "tags": ["过长的标签名字ABCDEFG", "导数", "导数"],
            }
        ]

    monkeypatch.setattr("app.services.ai_extractor._call_openai", fake_openai)

    long_text = "题干与答案\\n" * 2000  # 超出单段长度，触发拆分
    result, warnings, meta = extract_questions_ai(user, long_text)

    assert len(calls) > 1  # 确认发生了分段调用
    assert len(result) == len(calls)
    assert result[0].index == 1
    assert result[-1].index == len(calls)
    assert all(item.tags for item in result)
    assert all(len(item.tags) <= 3 for item in result)
    assert all(len(tag) <= 12 for item in result for tag in item.tags)
    assert warnings and "拆分" in warnings[0]
    assert meta["stats"]["processed_segments"] == len(calls)
    assert meta["stats"]["tag_source"] == "ai"


def test_extract_questions_ai_normalizes_tags(monkeypatch):
    user = User(
        id=5,
        username="tags",
        email="tags@example.com",
        hashed_password="hash",
    )
    user.settings = UserSettings(
        user_id=5,
        ai_provider="openai",
        ai_model="gpt-test",
        encrypted_api_key=encrypt_api_key("sk-tag"),
    )

    def fake_openai(model: str, api_key: str, text: str):
        return [
            {
                "index": 1,
                "question": "标签测试题",
                "question_type": "short_answer",
                "answer": "42",
                "tags": [
                    "  导数概念  ",
                    "",
                    "概率统计",
                    "过长的标签名字ABCDEFG",
                    "重复",
                    "REPEAT",
                ],
            }
        ]

    monkeypatch.setattr("app.services.ai_extractor._call_openai", fake_openai)

    result, warnings, meta = extract_questions_ai(user, "题干")
    assert warnings == []
    assert meta["stats"]["tag_source"] == "ai"
    assert len(result) == 1
    assert result[0].tags[:2] == ["导数概念", "概率统计"]
    assert len(result[0].tags) == 3
    assert all(len(tag) <= 12 for tag in result[0].tags)


def test_extract_questions_ai_fallback(monkeypatch):
    user = User(
        id=3,
        username="fallback",
        email="fallback@example.com",
        hashed_password="hash",
    )
    user.settings = UserSettings(
        user_id=3,
        ai_provider="openai",
        ai_model="gpt-test",
        encrypted_api_key=encrypt_api_key("sk-test"),
    )

    def fake_openai(model: str, api_key: str, text: str):
        raise HTTPException(status_code=502, detail="timeout")

    monkeypatch.setattr("app.services.ai_extractor._call_openai", fake_openai)

    sample = "1. 题目一\\n答案：A\\n2. 题目二\\n答案：B"
    result, warnings, meta = extract_questions_ai(user, sample)

    assert len(result) >= 1
    assert "题目一" in result[0].question
    assert result[0].tags == []
    assert any("回退到规则解析" in w for w in warnings)
    assert meta["stats"]["processed_segments"] >= 1


def test_extract_json_handles_control_char():
    payload = (
        '{"questions": [{"index": 1, "question": "Q1", '
        '"question_type": "short_answer", "options": [], '
        '"answer": "A", "explanation": "line1 \\u000b line2", "tags": ["集合论"]}]}'
    )
    result = _extract_json(payload)
    assert isinstance(result, list)
    assert result[0]["question"] == "Q1"
