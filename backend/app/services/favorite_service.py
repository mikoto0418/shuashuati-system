"""Favorite question service functions."""
from typing import List

from sqlalchemy.orm import Session

from app.models.favorite import Favorite
from app.models.question import Question


def list_favorites(db: Session, user_id: int) -> List[Favorite]:
    return (
        db.query(Favorite)
        .filter(Favorite.user_id == user_id)
        .order_by(Favorite.created_at.desc())
        .all()
    )


def add_favorite(db: Session, user_id: int, question_id: int) -> Favorite:
    existing = (
        db.query(Favorite)
        .filter(
            Favorite.user_id == user_id,
            Favorite.question_id == question_id,
        )
        .first()
    )
    if existing:
        return existing

    favorite = Favorite(user_id=user_id, question_id=question_id)
    db.add(favorite)
    db.commit()
    db.refresh(favorite)
    return favorite


def remove_favorite(db: Session, user_id: int, question_id: int) -> None:
    favorite = (
        db.query(Favorite)
        .filter(
            Favorite.user_id == user_id,
            Favorite.question_id == question_id,
        )
        .first()
    )
    if favorite is None:
        raise LookupError("Favorite not found")
    db.delete(favorite)
    db.commit()


def favorite_to_dict(favorite: Favorite) -> dict:
    question: Question = favorite.question
    return {
        "question_id": favorite.question_id,
        "question": question.question,
        "question_type": question.question_type,
        "options": question.options or [],
        "answer": question.answer,
        "explanation": question.explanation,
        "created_at": favorite.created_at,
        "category_id": question.category_id,
        "category_name": question.category.name if question.category else None,
    }
