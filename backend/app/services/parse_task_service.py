"""
AI 解析任务服务。
"""
from __future__ import annotations

import json
import time
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

from fastapi import HTTPException, UploadFile
from fastapi.background import BackgroundTasks
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import SessionLocal
from app.models.ai_task import AITask, AITaskStatus
from app.models.category import Category
from app.models.user import User
from app.models.question import Question
from app.services.file_service import store_upload_file
from app.services.question_parser import (
    parse_questions,
    ParsedOption,
    ParsedQuestion,
)
from app.services.ai_extractor import extract_questions_ai
from app.services import question_importer
from app.schemas.ai_task import AITaskStatusResponse, AITaskResult
from app.schemas.file import ParsedOptionSchema, ParsedQuestionSchema
from app.schemas.question import QuestionBatchCreateResponse
from app.utils.text_extractor import extract_text

RESULT_ROOT = Path(settings.UPLOAD_DIR) / "ai_results"
RESULT_ROOT.mkdir(parents=True, exist_ok=True)


def create_task(
    db: Session,
    user_id: int,
    upload_file: UploadFile,
    mode: str,
    background_tasks: BackgroundTasks,
) -> AITask:
    saved_path, original_name = store_upload_file(upload_file)
    task = AITask(
        user_id=user_id,
        file_path=str(saved_path),
        original_name=original_name,
        mode=mode,
        status=AITaskStatus.PENDING.value,
        progress=0.0,
    )
    db.add(task)
    db.commit()
    db.refresh(task)

    background_tasks.add_task(_run_task, task.id)
    return task


def _auto_import_questions(
    db: Session,
    task: AITask,
    questions: List[ParsedQuestionSchema],
) -> Optional[dict]:
    if not questions:
        return None

    category_name = Path(task.original_name).stem or f"导入任务-{task.id}"
    category = (
        db.query(Category)
        .filter(Category.user_id == task.user_id, Category.name == category_name)
        .first()
    )
    created_category = False
    if category is None:
        category = Category(user_id=task.user_id, name=category_name)
        db.add(category)
        db.commit()
        db.refresh(category)
        created_category = True

    import_result: QuestionBatchCreateResponse = question_importer.import_questions(
        db=db,
        user_id=task.user_id,
        parsed_questions=questions,
        category_id=category.id,
        source_file=task.file_path,
    )

    # 更新分类题目数量
    count = (
        db.query(func.count(Question.id))
        .filter(Question.category_id == category.id)
        .scalar()
    )
    category.question_count = count
    db.commit()

    return {
        "category_id": category.id,
        "category_name": category.name,
        "success": import_result.success_count,
        "failed": import_result.failed_count,
        "errors": import_result.errors,
        "created_category": created_category,
    }


def _persist_progress_state(
    db: Session,
    task: AITask,
    warnings: List[str],
    events: List[Dict[str, object]],
    stats: Dict[str, object],
) -> None:
    """将解析任务的阶段性状态写入数据库以供前端轮询展示。"""
    task.warning_message = json.dumps(
        {"warnings": warnings, "events": events, "stats": stats},
        ensure_ascii=False,
    )
    db.commit()


def _update_processing_progress(
    task: AITask, stats: Dict[str, object], pending_segments: int
) -> None:
    """根据分段处理进度动态更新任务进度区间（60%-85%）。"""
    stats["pending_segments"] = pending_segments
    processed = int(stats.get("processed_segments") or 0)
    total = processed + pending_segments
    if total <= 0:
        ratio = 1.0
    else:
        ratio = processed / total
    ratio = max(0.0, min(1.0, ratio))
    task.progress = 0.6 + 0.25 * ratio


def _run_task(task_id: int) -> None:
    with SessionLocal() as db:
        task = db.query(AITask).filter(AITask.id == task_id).first()
        if task is None:
            return
        start_time = time.perf_counter()
        events: List[Dict[str, object]] = []
        stats: Dict[str, object] = {}
        auto_import_summary: Optional[dict] = None

        task.status = AITaskStatus.RUNNING.value
        task.progress = 0.1
        db.commit()
        db.refresh(task)

        file_path = Path(task.file_path)
        if not file_path.exists():
            task.status = AITaskStatus.FAILED.value
            task.error_message = "原始文件不存在或已被删除。"
            task.progress = 1.0
            db.commit()
            return

        try:
            task.progress = 0.2
            db.commit()
            text = extract_text(file_path)
        except Exception as exc:  # noqa: BLE001
            task.status = AITaskStatus.FAILED.value
            task.error_message = f"解析文件失败：{exc}"
            task.progress = 1.0
            db.commit()
            return

        task.progress = 0.35

        parsed = parse_questions(text)
        use_ai = False
        warnings: List[str] = []
        events.append(
            {
                "type": "info",
                "message": f"预检规则解析识别 {len(parsed)} 题，当前模式：{task.mode}",
                "timestamp": datetime.utcnow().isoformat(),
            }
        )

        _persist_progress_state(db, task, warnings, events, stats)

        if task.mode == "ai":
            use_ai = True
        elif task.mode == "mixed":
            quality_ok, quality_warn = _assess_rule_quality(parsed)
            warnings.extend(quality_warn)
            if not quality_ok:
                use_ai = True
        else:
            quality_ok, quality_warn = _assess_rule_quality(parsed)
            warnings.extend(quality_warn)

        task.progress = 0.6
        _persist_progress_state(db, task, warnings, events, stats)

        try:
            if use_ai:
                user = db.query(User).filter(User.id == task.user_id).first()
                events.append(
                    {
                        "type": "info",
                        "message": "进入 AI 解析阶段，开始逐段处理文本。",
                        "timestamp": datetime.utcnow().isoformat(),
                    }
                )
                _persist_progress_state(db, task, warnings, events, stats)

                def _report_progress(
                    ai_warnings: List[str],
                    ai_events: List[Dict[str, object]],
                    ai_stats: Dict[str, object],
                ) -> None:
                    merged_stats = dict(stats)
                    merged_stats.update(ai_stats)
                    pending = int(ai_stats.get("pending_segments") or 0)
                    _update_processing_progress(task, merged_stats, pending)
                    combined_warnings = list(warnings) + list(ai_warnings)
                    combined_events = list(events) + list(ai_events)
                    _persist_progress_state(
                        db, task, combined_warnings, combined_events, merged_stats
                    )

                questions, ai_warnings, extract_meta = extract_questions_ai(
                    user, text, reporter=_report_progress
                )
                warnings.extend(ai_warnings)
                stats.update(extract_meta.get("stats", {}))
                events.extend(extract_meta.get("events", []))
                _update_processing_progress(
                    task, stats, int(stats.get("pending_segments") or 0)
                )
                _persist_progress_state(db, task, warnings, events, stats)
            else:
                questions = _convert_rule_parsed(parsed)
                stats.update(
                    {
                        "initial_segments": 1,
                        "processed_segments": 1,
                        "auto_split_segments": 0,
                        "provider": "rule",
                        "tag_source": "rule",
                    }
                )
                events.append(
                    {
                        "type": "segment",
                        "segment": 1,
                        "status": "rule",
                        "elapsed": 0.0,
                        "message": f"规则解析共识别 {len(questions)} 题。",
                        "timestamp": datetime.utcnow().isoformat(),
                    }
                )
                _update_processing_progress(task, stats, 0)
                _persist_progress_state(db, task, warnings, events, stats)
        except HTTPException as exc:
            if not use_ai and parsed:
                questions = _convert_rule_parsed(parsed)
                warnings.append(f"AI 解析失败：{exc.detail}")
                _update_processing_progress(task, stats, 0)
                _persist_progress_state(db, task, warnings, events, stats)
            else:
                task.status = AITaskStatus.FAILED.value
                task.error_message = str(exc.detail)
                task.progress = 1.0
                db.commit()
                return

        auto_imported = False
        if questions:
            task.progress = 0.85
            _persist_progress_state(db, task, warnings, events, stats)
            try:
                summary = _auto_import_questions(db, task, questions)
                if summary:
                    auto_import_summary = summary
                    auto_imported = summary["success"] > 0
                    warnings.append(
                        f"已自动导入 {summary['success']} 道题目至分类「{summary['category_name']}」。"
                    )
                    if summary["failed"]:
                        warnings.append(
                            f"自动导入失败 {summary['failed']} 道题目，已记录至导入日志。"
                        )
                    events.append(
                        {
                            "type": "import",
                            "message": (
                                f"自动导入完成：分类「{summary['category_name']}」 "
                                f"成功 {summary['success']} 题，失败 {summary['failed']} 题"
                            ),
                            "timestamp": datetime.utcnow().isoformat(),
                        }
                    )
                    _persist_progress_state(db, task, warnings, events, stats)
            except Exception as exc:  # noqa: BLE001
                warnings.append(f"自动导入题目时出现问题：{exc}")
                events.append(
                    {
                        "type": "warning",
                        "message": f"自动导入题目失败：{exc}",
                        "timestamp": datetime.utcnow().isoformat(),
                    }
                )
                _persist_progress_state(db, task, warnings, events, stats)

        stats["parsed_questions"] = len(questions)

        result_payload = {
            "questions": [question.model_dump() for question in questions],
            "warnings": warnings,
            "original_name": task.original_name,
            "file_path": task.file_path,
            "used_ai": use_ai,
            "auto_imported": auto_imported,
            "import_summary": auto_import_summary,
            "stats": stats,
            "events": events,
        }

        task.progress = 0.9
        result_path = RESULT_ROOT / f"{uuid.uuid4()}.json"
        result_path.write_text(
            json.dumps(result_payload, ensure_ascii=False),
            encoding="utf-8",
        )

        elapsed = time.perf_counter() - start_time
        stats["duration_seconds"] = round(elapsed, 2)
        stats["auto_imported"] = auto_imported
        if auto_import_summary:
            stats["import_summary"] = auto_import_summary
        events.append(
            {
                "type": "info",
                "message": f"任务完成，用时 {stats['duration_seconds']} 秒，共生成 {len(questions)} 题。",
                "timestamp": datetime.utcnow().isoformat(),
            }
        )

        task.result_path = str(result_path)
        task.status = AITaskStatus.SUCCESS.value
        task.progress = 1.0
        task.warning_message = json.dumps(
            {
                "warnings": warnings,
                "events": events,
                "stats": stats,
            },
            ensure_ascii=False,
        )
        db.commit()


def to_status_response(task: AITask) -> AITaskStatusResponse:
    warnings: List[str] = []
    stats: Optional[Dict[str, object]] = None
    events: List[Dict[str, object]] = []
    if task.warning_message:
        try:
            payload = json.loads(task.warning_message)
            if isinstance(payload, dict):
                warnings = payload.get("warnings") or []
                stats = payload.get("stats")
                events = payload.get("events") or []
            elif isinstance(payload, list):
                warnings = payload
            else:
                warnings = [task.warning_message]
        except json.JSONDecodeError:
            warnings = [task.warning_message]
    return AITaskStatusResponse(
        id=task.id,
        status=task.status,
        progress=task.progress,
        mode=task.mode,
        original_name=task.original_name,
        file_path=task.file_path,
        warnings=warnings,
        error=task.error_message,
        stats=stats,
        events=events,
        created_at=task.created_at,
        updated_at=task.updated_at,
    )


def get_task(db: Session, user_id: int, task_id: int) -> Optional[AITask]:
    return (
        db.query(AITask)
        .filter(AITask.id == task_id, AITask.user_id == user_id)
        .first()
    )


def list_tasks(db: Session, user_id: int) -> List[AITask]:
    return (
        db.query(AITask)
        .filter(AITask.user_id == user_id)
        .order_by(AITask.created_at.desc())
        .limit(20)
        .all()
    )


def load_task_result(
    db: Session,
    user_id: int,
    task_id: int,
) -> Optional[AITaskResult]:
    task = get_task(db, user_id, task_id)
    if task is None or task.status != AITaskStatus.SUCCESS.value or not task.result_path:
        return None
    result_path = Path(task.result_path)
    try:
        raw = result_path.read_text(encoding="utf-8")
    except FileNotFoundError:
        task.status = AITaskStatus.FAILED.value
        task.error_message = "结果文件已丢失，请重新提交解析任务。"
        task.progress = 1.0
        db.commit()
        return None
    data = json.loads(raw)
    return AITaskResult(
        id=task.id,
        status=task.status,
        questions=data.get("questions") or [],
        warnings=data.get("warnings") or [],
        original_name=data.get("original_name") or task.original_name,
        file_path=data.get("file_path") or task.file_path,
        used_ai=bool(data.get("used_ai")),
        stats=data.get("stats"),
        events=data.get("events") or [],
        auto_imported=bool(data.get("auto_imported")),
        import_summary=data.get("import_summary"),
    )


def _convert_rule_parsed(parsed: List[ParsedQuestion]) -> List[ParsedQuestionSchema]:
    result: List[ParsedQuestionSchema] = []
    for item in parsed:
        options = [
            ParsedOptionSchema(key=opt.key, content=opt.content)
            for opt in (item.options or [])
        ]
        result.append(
            ParsedQuestionSchema(
                index=item.index,
                question=item.question,
                question_type=item.question_type,
                options=options,
                answer=item.answer,
                explanation=item.explanation,
                raw_text=item.raw_text,
                tags=[],
            )
        )
    return result


def _assess_rule_quality(parsed: List[ParsedQuestion]) -> tuple[bool, List[str]]:
    if not parsed:
        return False, ["未识别到题目，已尝试调用 AI 解析。"]
    total = len(parsed)
    valid = 0
    for item in parsed:
        question = (item.question or "").strip()
        answer = (item.answer or "").strip()
        if not question or not answer:
            continue
        options: List[ParsedOption] = item.options or []
        if options:
            cleaned = [opt.content.strip() for opt in options if opt.content.strip()]
            if not cleaned:
                continue
            if any(len(opt) > 200 for opt in cleaned):
                continue
            if any(" | " in opt for opt in cleaned):
                continue
        valid += 1
    quality = valid / total
    if quality >= 0.6:
        return True, []
    return False, ["规则解析质量较差，已尝试调用 AI 改进结果。"]
