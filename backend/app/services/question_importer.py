"""题目导入服务"""
from __future__ import annotations

from typing import List, Optional

from sqlalchemy.orm import Session

from app.models.question import Question
from app.schemas.file import ParsedOptionSchema, ParsedQuestionSchema
from app.schemas.question import (
    QuestionBatchCreateResponse,
    QuestionImportItemResult,
)


def _normalize_options(options: List[ParsedOptionSchema]) -> List[str]:
    return [f"{opt.key}. {opt.content}" for opt in options]


def import_questions(
    db: Session,
    user_id: int,
    parsed_questions: List[ParsedQuestionSchema],
    category_id: Optional[int] = None,
    source_file: Optional[str] = None,
) -> QuestionBatchCreateResponse:
    total = len(parsed_questions)
    created_entities: List[Question] = []
    result_items: List[QuestionImportItemResult] = []
    success_entries: List[QuestionImportItemResult] = []
    errors: List[str] = []

    for item in parsed_questions:
        question_text = (item.question or "").strip()
        answer_text = (item.answer or "").strip()
        question_type = item.question_type or "short_answer"

        if not question_text or not answer_text:
            message = f"题目 {item.index} 缺少题干或答案"
            errors.append(message)
            result_items.append(
                QuestionImportItemResult(
                    index=item.index,
                    question=question_text,
                    question_type=question_type,
                    answer=answer_text,
                    status="failed",
                    message=message,
                    question_id=None,
                    tags=[],
                )
            )
            continue

        options = _normalize_options(item.options) if item.options else None
        if options:
            cleaned = [opt.strip() for opt in options if opt.strip()]
            if not cleaned:
                message = f"题目 {item.index} 选项内容为空"
                errors.append(message)
                result_items.append(
                    QuestionImportItemResult(
                        index=item.index,
                        question=question_text,
                        question_type=question_type,
                        answer=answer_text,
                        status="failed",
                        message=message,
                        question_id=None,
                        tags=[],
                    )
                )
                continue
            if any(len(opt) > 300 for opt in cleaned):
                message = f"题目 {item.index} 选项格式异常"
                errors.append(message)
                result_items.append(
                    QuestionImportItemResult(
                        index=item.index,
                        question=question_text,
                        question_type=question_type,
                        answer=answer_text,
                        status="failed",
                        message=message,
                        question_id=None,
                        tags=[],
                    )
                )
                continue

        cleaned_tags = [
            tag.strip()
            for tag in (item.tags or [])
            if isinstance(tag, str) and tag.strip()
        ]
        entity = Question(
            user_id=user_id,
            category_id=category_id,
            question=question_text,
            question_type=question_type,
            options=options,
            answer=answer_text,
            explanation=item.explanation or "",
            source_file=source_file,
            tags=cleaned_tags,
        )
        created_entities.append(entity)
        placeholder = QuestionImportItemResult(
            index=item.index,
            question=question_text,
            question_type=question_type,
            answer=answer_text,
            status="success",
            message=None,
            question_id=None,
            tags=cleaned_tags,
        )
        result_items.append(placeholder)
        success_entries.append(placeholder)

    if not created_entities:
        return QuestionBatchCreateResponse(
            success_count=0,
            failed_count=total,
            created_ids=[],
            errors=errors,
            items=result_items,
        )

    for entity in created_entities:
        db.add(entity)

    db.commit()
    for entity in created_entities:
        db.refresh(entity)

    for entity, placeholder in zip(created_entities, success_entries):
        placeholder.question_id = entity.id

    return QuestionBatchCreateResponse(
        success_count=len(created_entities),
        failed_count=total - len(created_entities),
        created_ids=[entity.id for entity in created_entities],
        errors=errors,
        items=result_items,
    )
