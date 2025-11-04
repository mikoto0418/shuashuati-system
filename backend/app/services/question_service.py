"""
Question service functions.
"""
from typing import List, Optional, Sequence

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.category import Category
from app.models.question import Question
from app.schemas.question import (
    QuestionCreate,
    QuestionListItem,
    QuestionResponse,
    QuestionUpdate,
)
from app.services.file_service import remove_static_file


def _update_category_count(
    db: Session, old_category_id: Optional[int], new_category_id: Optional[int]
) -> None:
    for category_id in {old_category_id, new_category_id}:
        if category_id is None:
            continue
        count = (
            db.query(func.count(Question.id))
            .filter(Question.category_id == category_id)
            .scalar()
        )
        db.query(Category).filter(Category.id == category_id).update(
            {"question_count": count}, synchronize_session=False
        )


def _ensure_category_owner(
    db: Session, user_id: int, category_id: Optional[int]
) -> None:
    if category_id is None:
        return
    exists = (
        db.query(Category)
        .filter(Category.id == category_id, Category.user_id == user_id)
        .first()
    )
    if exists is None:
        raise ValueError("Category not found")


def list_questions(
    db: Session,
    user_id: int,
    page: int,
    page_size: int,
    keyword: Optional[str] = None,
    category_id: Optional[int] = None,
) -> tuple[int, Sequence[Question]]:
    query = db.query(Question).filter(Question.user_id == user_id)

    if keyword:
        like = f"%{keyword.strip()}%"
        query = query.filter(Question.question.ilike(like))
    if category_id:
        query = query.filter(Question.category_id == category_id)

    total = query.count()
    items = (
        query.order_by(Question.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )
    return total, items


def get_question(db: Session, user_id: int, question_id: int) -> Question:
    question = (
        db.query(Question)
        .filter(Question.id == question_id, Question.user_id == user_id)
        .first()
    )
    if question is None:
        raise LookupError("Question not found")
    return question


def create_question(
    db: Session, user_id: int, payload: QuestionCreate
) -> Question:
    _ensure_category_owner(db, user_id, payload.category_id)

    question = Question(
        user_id=user_id,
        question=payload.question.strip(),
        question_type=payload.question_type,
        options=payload.options,
        answer=payload.answer.strip(),
        explanation=(payload.explanation or "").strip(),
        image_url=payload.image_url,
        tags=payload.tags,
        category_id=payload.category_id,
        source_file=payload.source_file,
    )
    db.add(question)
    db.commit()
    db.refresh(question)

    _update_category_count(db, None, question.category_id)
    db.commit()
    db.refresh(question)
    return question


def update_question(
    db: Session, user_id: int, question_id: int, payload: QuestionUpdate
) -> Question:
    question = get_question(db, user_id, question_id)
    old_category_id = question.category_id
    old_image_url = question.image_url
    if payload.category_id is not None:
        _ensure_category_owner(db, user_id, payload.category_id)

    updates = payload.model_dump(exclude_unset=True)
    for field, value in updates.items():
        setattr(question, field, value)

    db.commit()
    db.refresh(question)
    _update_category_count(db, old_category_id, question.category_id)
    db.commit()
    db.refresh(question)

    if "image_url" in updates and old_image_url and old_image_url != question.image_url:
        remove_static_file(old_image_url)

    return question


def delete_question(db: Session, user_id: int, question_id: int) -> None:
    question = get_question(db, user_id, question_id)
    category_id = question.category_id
    image_url = question.image_url
    db.delete(question)
    db.commit()
    _update_category_count(db, category_id, None)
    db.commit()
    remove_static_file(image_url)


def delete_questions_batch(
    db: Session, user_id: int, question_ids: List[int]
) -> int:
    questions = (
        db.query(Question)
        .filter(Question.user_id == user_id, Question.id.in_(question_ids))
        .all()
    )
    categories = {q.category_id for q in questions}
    image_urls = [q.image_url for q in questions if q.image_url]
    deleted = len(questions)
    for question in questions:
        db.delete(question)
    db.commit()
    for category_id in categories:
        _update_category_count(db, category_id, None)
    db.commit()
    for image_url in image_urls:
        remove_static_file(image_url)
    return deleted


def to_list_item(question: Question) -> QuestionListItem:
    category_name = question.category.name if question.category else None
    has_image = bool(question.image_url)
    return QuestionListItem.model_validate(
        {
            "id": question.id,
            "question": question.question,
            "question_type": question.question_type,
            "answer": question.answer,
            "category_id": question.category_id,
            "category_name": category_name,
            "practice_count": question.practice_count,
            "correct_count": question.correct_count,
            "correct_rate": question.correct_rate if hasattr(question, "correct_rate") else 0.0,
            "has_image": has_image,
            "created_at": question.created_at,
        }
    )


def to_response(question: Question) -> QuestionResponse:
    category_name = question.category.name if question.category else None
    return QuestionResponse.model_validate(
        {
            "id": question.id,
            "user_id": question.user_id,
            "question": question.question,
            "question_type": question.question_type,
            "options": question.options,
            "answer": question.answer,
            "explanation": question.explanation,
            "tags": question.tags,
            "category_id": question.category_id,
            "category_name": category_name,
            "image_url": question.image_url,
            "source_file": question.source_file,
            "practice_count": question.practice_count,
            "correct_count": question.correct_count,
            "correct_rate": question.correct_count / question.practice_count
            if question.practice_count
            else 0.0,
            "created_at": question.created_at,
            "updated_at": question.updated_at,
        }
    )
