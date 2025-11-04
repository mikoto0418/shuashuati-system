"""Wrong question service functions."""
from typing import List

from sqlalchemy.orm import Session

from app.models.favorite import WrongQuestion
from app.models.question import Question


def list_wrong_questions(db: Session, user_id: int) -> List[WrongQuestion]:
    return (
        db.query(WrongQuestion)
        .filter(WrongQuestion.user_id == user_id)
        .order_by(WrongQuestion.last_wrong_time.desc())
        .all()
    )


def delete_wrong_question(db: Session, user_id: int, question_id: int) -> None:
    record = (
        db.query(WrongQuestion)
        .filter(
            WrongQuestion.user_id == user_id,
            WrongQuestion.question_id == question_id,
        )
        .first()
    )
    if record is None:
        raise LookupError("Wrong question not found")
    db.delete(record)
    db.commit()


def wrong_question_to_dict(record: WrongQuestion) -> dict:
    question: Question = record.question
    return {
        "question_id": record.question_id,
        "question": question.question,
        "question_type": question.question_type,
        "options": question.options or [],
        "answer": question.answer,
        "explanation": question.explanation,
        "wrong_count": record.wrong_count,
        "last_wrong_time": record.last_wrong_time,
        "category_id": question.category_id,
        "category_name": question.category.name if question.category else None,
    }
