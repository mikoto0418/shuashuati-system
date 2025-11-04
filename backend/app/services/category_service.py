"""
Category service functions.
"""
from typing import List, Optional

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.category import Category
from app.models.question import Question
from app.schemas.question import (
    CategoryCreate,
    CategoryResponse,
    CategoryUpdate,
)


def list_categories(db: Session, user_id: int) -> List[Category]:
    return (
        db.query(Category)
        .filter(Category.user_id == user_id)
        .order_by(Category.created_at.desc())
        .all()
    )


def _refresh_question_count(db: Session, category_id: Optional[int]) -> None:
    if category_id is None:
        return
    count = (
        db.query(func.count(Question.id))
        .filter(Question.category_id == category_id)
        .scalar()
    )
    db.query(Category).filter(Category.id == category_id).update(
        {"question_count": count}, synchronize_session=False
    )


def create_category(db: Session, user_id: int, payload: CategoryCreate) -> Category:
    exists = (
        db.query(Category)
        .filter(Category.user_id == user_id, Category.name == payload.name)
        .first()
    )
    if exists:
        raise ValueError("Category name already exists")

    category = Category(
        user_id=user_id,
        name=payload.name,
        description=payload.description,
        parent_id=payload.parent_id,
    )
    db.add(category)
    db.commit()
    db.refresh(category)
    return category


def update_category(
    db: Session, user_id: int, category_id: int, payload: CategoryUpdate
) -> Category:
    category = (
        db.query(Category)
        .filter(Category.id == category_id, Category.user_id == user_id)
        .first()
    )
    if category is None:
        raise LookupError("Category not found")

    if payload.name and payload.name != category.name:
        duplicate = (
            db.query(Category)
            .filter(Category.user_id == user_id, Category.name == payload.name)
            .first()
        )
        if duplicate:
            raise ValueError("Category name already exists")

    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(category, field, value)

    db.commit()
    db.refresh(category)
    return category


def delete_category(db: Session, user_id: int, category_id: int) -> None:
    category = (
        db.query(Category)
        .filter(Category.id == category_id, Category.user_id == user_id)
        .first()
    )
    if category is None:
        raise LookupError("Category not found")

    db.query(Question).filter(Question.category_id == category_id).update(
        {"category_id": None}, synchronize_session=False
    )

    db.delete(category)
    db.commit()


def to_response(category: Category) -> CategoryResponse:
    return CategoryResponse.model_validate(category)

