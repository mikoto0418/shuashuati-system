"""
Dashboard 统计服务。
"""
from __future__ import annotations

from datetime import datetime

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.favorite import Favorite, WrongQuestion
from app.models.import_batch import ImportBatch
from app.models.practice import PracticeAnswer, PracticeSession


def _scalar_or_zero(query) -> int:
    value = query.scalar()
    return int(value or 0)


def _practice_answer_count_query(db: Session, user_id: int):
    return (
        db.query(func.count(PracticeAnswer.id))
        .join(PracticeSession, PracticeAnswer.session_id == PracticeSession.id)
        .filter(PracticeSession.user_id == user_id)
    )


def get_dashboard_stats(db: Session, user_id: int) -> dict[str, float | int]:
    """
    计算仪表盘各项统计指标。
    """

    today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)

    total_practice_questions = _scalar_or_zero(
        _practice_answer_count_query(db, user_id)
    )

    today_completed = _scalar_or_zero(
        _practice_answer_count_query(db, user_id).filter(
            PracticeAnswer.answer_time >= today_start
        )
    )

    today_correct = _scalar_or_zero(
        db.query(func.count(PracticeAnswer.id))
        .join(PracticeSession, PracticeAnswer.session_id == PracticeSession.id)
        .filter(
            PracticeSession.user_id == user_id,
            PracticeAnswer.answer_time >= today_start,
            PracticeAnswer.is_correct.is_(True),
        )
    )

    today_accuracy = (
        today_correct / today_completed if today_completed > 0 else 0.0
    )

    pending_wrong_questions = _scalar_or_zero(
        db.query(func.count(WrongQuestion.id)).filter(WrongQuestion.user_id == user_id)
    )

    total_favorites = _scalar_or_zero(
        db.query(func.count(Favorite.id)).filter(Favorite.user_id == user_id)
    )

    ai_parse_count = _scalar_or_zero(
        db.query(func.count(ImportBatch.id)).filter(
            ImportBatch.user_id == user_id, ImportBatch.used_ai.is_(True)
        )
    )

    return {
        "today_completed": today_completed,
        "today_accuracy": round(today_accuracy, 4),
        "pending_wrong_questions": pending_wrong_questions,
        "total_practice_questions": total_practice_questions,
        "total_favorites": total_favorites,
        "ai_parse_count": ai_parse_count,
    }
