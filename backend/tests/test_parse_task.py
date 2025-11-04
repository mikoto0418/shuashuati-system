"""AI 解析后台任务测试。"""
from __future__ import annotations

import io
from typing import Iterable

import pytest
from fastapi import BackgroundTasks, HTTPException
from starlette.datastructures import UploadFile

from app.core.config import settings
from app.models.ai_task import AITask, AITaskStatus
from app.models.user import User
from app.models.question import Question
from app.models.category import Category
from app.services import parse_task_service
from .conftest import TestingSessionLocal


@pytest.fixture(autouse=True)
def _patch_session_factory(monkeypatch: pytest.MonkeyPatch) -> Iterable[None]:
    """强制解析任务服务使用测试数据库。"""
    monkeypatch.setattr(parse_task_service, "SessionLocal", TestingSessionLocal)
    yield


@pytest.fixture
def temp_upload_dir(tmp_path, monkeypatch: pytest.MonkeyPatch):
    """为测试重定向上传与结果目录。"""
    monkeypatch.setattr(settings, "UPLOAD_DIR", str(tmp_path), raising=False)
    result_dir = tmp_path / "ai_results"
    result_dir.mkdir(parents=True, exist_ok=True)
    monkeypatch.setattr(parse_task_service, "RESULT_ROOT", result_dir, raising=False)
    yield tmp_path


def test_parse_task_basic_success(temp_upload_dir):
    """basic 模式：规则解析成功应完成任务并写入结果。"""
    background = BackgroundTasks()
    upload = UploadFile(
        filename="sample.txt",
        file=io.BytesIO("1. 第一题\n答案：A".encode("utf-8")),
    )

    with TestingSessionLocal() as db:
        user = User(
            username="task_basic",
            email="task_basic@example.com",
            hashed_password="hash",
        )
        db.add(user)
        db.commit()
        db.refresh(user)

        task = parse_task_service.create_task(
            db=db,
            user_id=user.id,
            upload_file=upload,
            mode="basic",
            background_tasks=background,
        )
        task_id = task.id
        parse_task_service._run_task(task_id)

    with TestingSessionLocal() as db:
        stored = db.get(AITask, task_id)
        assert stored is not None
        assert stored.status == AITaskStatus.SUCCESS.value
        assert stored.progress == pytest.approx(1.0)
        status_snapshot = parse_task_service.to_status_response(stored)
        assert status_snapshot.events
        assert status_snapshot.stats is not None
        assert status_snapshot.stats.get("parsed_questions") == 1
        assert status_snapshot.progress == pytest.approx(1.0)
        result = parse_task_service.load_task_result(db, stored.user_id, task_id)
        category = db.query(Category).filter(Category.user_id == stored.user_id).first()
        questions = db.query(Question).filter(Question.user_id == stored.user_id).all()

    assert result is not None
    assert result.original_name == "sample.txt"
    assert result.file_path
    assert result.used_ai is False
    assert result.auto_imported is True
    assert result.import_summary is not None
    assert len(result.questions) == 1
    assert result.questions[0]["answer"] == "A"
    assert category is not None
    assert category.question_count == len(questions) == 1


def test_parse_task_mixed_ai_failure(temp_upload_dir, monkeypatch: pytest.MonkeyPatch):
    """mixed 模式：AI 分支失败且无规则结果时应标记失败并记录错误信息。"""

    def _raise_ai_error(*_args, **_kwargs):
        raise HTTPException(status_code=502, detail="AI 服务不可用")

    monkeypatch.setattr(
        parse_task_service, "extract_questions_ai", _raise_ai_error, raising=False
    )
    monkeypatch.setattr(
        parse_task_service, "parse_questions", lambda _text: [], raising=False
    )

    background = BackgroundTasks()
    upload = UploadFile(
        filename="broken.txt",
        file=io.BytesIO("没有题号的内容，需要 AI 解析".encode("utf-8")),
    )

    with TestingSessionLocal() as db:
        user = User(
            username="task_ai_fail",
            email="task_ai_fail@example.com",
            hashed_password="hash",
        )
        db.add(user)
        db.commit()
        db.refresh(user)

        task = parse_task_service.create_task(
            db=db,
            user_id=user.id,
            upload_file=upload,
            mode="mixed",
            background_tasks=background,
        )
        task_id = task.id
        parse_task_service._run_task(task_id)

    with TestingSessionLocal() as db:
        stored = db.get(AITask, task_id)
        assert stored is not None
        assert stored.status == AITaskStatus.FAILED.value
        assert stored.progress == pytest.approx(1.0)
        assert "AI 服务不可用" in (stored.error_message or "")
        result = parse_task_service.load_task_result(db, stored.user_id, task_id)

    assert result is None
