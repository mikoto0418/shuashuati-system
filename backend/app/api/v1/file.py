"""文件上传与题目提取路由."""
from __future__ import annotations

from pathlib import Path
from typing import Iterable, List, Sequence

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_active_user, get_db
from app.models.user import User
from app.schemas.file import (
    FileImportRequest,
    FileImportResult,
    FilePreviewResponse,
    ParsedOptionSchema,
    ParsedQuestionSchema,
)
from app.schemas.question import QuestionBatchCreateResponse
from app.services.ai_extractor import extract_questions_ai
from app.services import import_batch_service, question_importer
from app.services.file_service import store_upload_file
from app.services.question_parser import ParsedOption, ParsedQuestion, parse_questions
from app.utils.text_extractor import extract_text

router = APIRouter(prefix="/api/v1/file", tags=["File"])

ALLOWED_MODES = {"basic", "ai", "mixed"}
CHOICE_TYPES = {"single_choice", "multiple_choice"}


def _convert_rule_questions(
    questions: Sequence[ParsedQuestion],
) -> List[ParsedQuestionSchema]:
    def _map_option(option: ParsedOption) -> ParsedOptionSchema:
        return ParsedOptionSchema(key=option.key, content=option.content)

    converted: List[ParsedQuestionSchema] = []
    for item in questions:
        converted.append(
            ParsedQuestionSchema(
                index=item.index,
                question=item.question,
                question_type=item.question_type,
                options=[_map_option(opt) for opt in item.options],
                answer=item.answer,
                explanation=item.explanation,
                raw_text=item.raw_text,
            )
        )
    return converted


def _is_low_quality(questions: Iterable[ParsedQuestionSchema]) -> bool:
    questions = list(questions)
    if not questions:
        return True
    for item in questions:
        options = item.options or []
        if not item.answer:
            return True
        if item.question_type in CHOICE_TYPES and len(options) < 2:
            return True
    return False


def _rule_warnings(questions: Sequence[ParsedQuestionSchema]) -> List[str]:
    if questions:
        return []
    return ["未识别出有效题目，请检查题干格式或更换解析模式。"]


def _merge_stats(
    base: dict,
    extra: dict | None,
) -> dict:
    merged = dict(base)
    if extra:
        merged.update(extra)
    return merged


@router.post("/upload/preview", response_model=FilePreviewResponse)
async def upload_preview(
    upload_file: UploadFile = File(...),
    mode: str = Form("basic"),
    current_user: User = Depends(get_current_active_user),
) -> FilePreviewResponse:
    normalized_mode = mode.lower()
    if normalized_mode not in ALLOWED_MODES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="不支持的解析模式。"
        )

    saved_path, original_name = store_upload_file(upload_file)
    try:
        text = extract_text(saved_path)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)
        ) from exc

    rule_raw = parse_questions(text)
    rule_converted = _convert_rule_questions(rule_raw)

    warnings: List[str] = []
    events: List[dict] = []
    stats = {"mode": normalized_mode, "rule_questions": len(rule_converted)}

    questions: List[ParsedQuestionSchema]
    used_ai = False

    if normalized_mode == "ai":
        questions, ai_warnings, meta = extract_questions_ai(current_user, text)
        used_ai = True
        warnings.extend(ai_warnings)
        events.extend(meta.get("events") or [])
        stats = _merge_stats(stats, meta.get("stats"))
    elif normalized_mode == "mixed" and _is_low_quality(rule_converted):
        warnings.append("规则解析结果质量较弱，已自动切换到 AI 解析。")
        questions, ai_warnings, meta = extract_questions_ai(current_user, text)
        used_ai = True
        warnings.extend(ai_warnings)
        events.extend(meta.get("events") or [])
        stats = _merge_stats(stats, meta.get("stats"))
    else:
        questions = rule_converted
        warnings.extend(_rule_warnings(rule_converted))

    return FilePreviewResponse(
        file_path=str(saved_path),
        original_name=original_name or Path(saved_path).name,
        text=text,
        questions=questions,
        mode=normalized_mode,  # type: ignore[arg-type]
        used_ai=used_ai,
        warnings=warnings,
        stats=stats,
        events=events,
        auto_imported=False,
        import_summary=None,
    )


@router.post("/upload/confirm", response_model=FileImportResult)
async def confirm_import(
    payload: FileImportRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> FileImportResult:
    if not payload.questions:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="题目列表不能为空。"
        )

    result: QuestionBatchCreateResponse = question_importer.import_questions(
        db=db,
        user_id=current_user.id,
        parsed_questions=payload.questions,
        category_id=payload.category_id,
        source_file=payload.file_path,
    )

    batch = import_batch_service.create_batch(
        db=db,
        user_id=current_user.id,
        mode=payload.mode,
        original_name=payload.original_name
        or Path(payload.file_path).name,
        file_path=payload.file_path,
        used_ai=payload.used_ai,
        warnings=payload.warnings,
        stats=payload.stats,
        total_count=len(payload.questions),
    )
    result.batch_id = batch.id
    import_batch_service.register_items(db, batch, result.items)

    return FileImportResult(
        success_count=result.success_count,
        failed_count=result.failed_count,
        created_ids=result.created_ids,
        errors=result.errors,
    )
