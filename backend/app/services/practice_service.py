"""练习流程服务."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from random import shuffle
from typing import Dict, Iterable, List, Sequence, Tuple

from sqlalchemy.orm import Session

from app.models.favorite import Favorite, WrongQuestion
from app.models.practice import PracticeAnswer, PracticeSession
from app.models.question import Question

MAX_QUESTIONS_PER_SESSION = 50
MAX_HISTORY_PAGE_SIZE = 50


@dataclass(frozen=True)
class SessionStartResult:
    """开始练习结果."""

    session: PracticeSession
    questions: Sequence[Question]


def _filter_questions(
    db: Session,
    user_id: int,
    mode: str,
    category_ids: Iterable[int] | None,
    question_types: Iterable[str] | None,
) -> List[Question]:
    query = db.query(Question).filter(Question.user_id == user_id)

    if category_ids:
        query = query.filter(Question.category_id.in_(list(category_ids)))
    if question_types:
        query = query.filter(Question.question_type.in_(list(question_types)))

    if mode == "wrong":
        query = (
            query.join(WrongQuestion, WrongQuestion.question_id == Question.id)
            .filter(WrongQuestion.user_id == user_id)
            .order_by(WrongQuestion.last_wrong_time.desc())
        )
    elif mode == "favorite":
        query = (
            query.join(Favorite, Favorite.question_id == Question.id)
            .filter(Favorite.user_id == user_id)
            .order_by(Favorite.created_at.desc())
        )
    else:
        query = query.order_by(Question.created_at.asc())

    records: List[Question] = query.all()
    if mode == "random":
        shuffle(records)
    return records


def start_session(
    db: Session,
    user_id: int,
    mode: str,
    category_ids: Iterable[int] | None = None,
    question_types: Iterable[str] | None = None,
    question_ids: Iterable[int] | None = None,
) -> SessionStartResult:
    """启动新的练习会话."""
    selected: List[Question]
    ordered_ids: List[int]

    if question_ids:
        ordered_ids = list(dict.fromkeys(question_ids))[:MAX_QUESTIONS_PER_SESSION]
        selected_map = {
            q.id: q
            for q in db.query(Question)
            .filter(Question.user_id == user_id, Question.id.in_(ordered_ids))
            .all()
        }
        missing = [qid for qid in ordered_ids if qid not in selected_map]
        if missing:
            raise ValueError("存在无效的题目选择，请重新确认。")
        selected = [selected_map[qid] for qid in ordered_ids]
    else:
        candidates = _filter_questions(db, user_id, mode, category_ids, question_types)
        if not candidates:
            raise ValueError("暂无符合条件的题目，可调整筛选条件后重试。")
        selected = candidates[:MAX_QUESTIONS_PER_SESSION]
        ordered_ids = [question.id for question in selected]

    session = PracticeSession(
        user_id=user_id,
        mode=mode,
        category_ids=list(category_ids) if category_ids else None,
        question_types=list(question_types) if question_types else None,
        question_ids=ordered_ids,
        total_count=len(ordered_ids),
        start_time=datetime.utcnow(),
    )
    db.add(session)
    db.commit()
    db.refresh(session)

    return SessionStartResult(session=session, questions=selected)


def preview_questions(
    db: Session,
    user_id: int,
    mode: str,
    category_ids: Iterable[int] | None = None,
    question_types: Iterable[str] | None = None,
) -> tuple[int, List[Question]]:
    """根据筛选条件预览题目列表（不创建会话）。"""
    candidates = _filter_questions(db, user_id, mode, category_ids, question_types)
    return len(candidates), candidates[:MAX_QUESTIONS_PER_SESSION]


def _normalize_answer(answer: str | None) -> str:
    return (answer or "").strip()


def _update_question_stats(
    question: Question,
    was_correct: bool | None,
    is_correct: bool,
) -> None:
    if was_correct is None:
        question.practice_count += 1
        if is_correct:
            question.correct_count += 1
        return

    if was_correct and not is_correct:
        question.correct_count = max(question.correct_count - 1, 0)
    elif not was_correct and is_correct:
        question.correct_count += 1


def _update_session_stats(
    session: PracticeSession,
    was_correct: bool | None,
    is_correct: bool,
) -> None:
    if was_correct is None:
        if is_correct:
            session.correct_count += 1
        return

    if was_correct and not is_correct:
        session.correct_count = max(session.correct_count - 1, 0)
    elif not was_correct and is_correct:
        session.correct_count += 1


def _upsert_wrong_question(
    db: Session, user_id: int, question_id: int, is_correct: bool
) -> None:
    record = (
        db.query(WrongQuestion)
        .filter(
            WrongQuestion.user_id == user_id,
            WrongQuestion.question_id == question_id,
        )
        .first()
    )
    if is_correct:
        if record is not None:
            db.delete(record)
        return

    if record is None:
        record = WrongQuestion(user_id=user_id, question_id=question_id, wrong_count=1)
        db.add(record)
    else:
        record.wrong_count += 1
        record.last_wrong_time = datetime.utcnow()


def submit_answer(
    db: Session,
    user_id: int,
    session_id: int,
    question_id: int,
    user_answer: str | None,
) -> Tuple[PracticeAnswer, Question, PracticeSession]:
    """记录答题结果."""
    session = (
        db.query(PracticeSession)
        .filter(
            PracticeSession.id == session_id,
            PracticeSession.user_id == user_id,
        )
        .first()
    )
    if session is None:
        raise LookupError("练习会话不存在。")
    if question_id not in session.question_ids:
        raise ValueError("题目不属于当前练习会话。")

    question = (
        db.query(Question)
        .filter(Question.id == question_id, Question.user_id == user_id)
        .first()
    )
    if question is None:
        raise LookupError("题目不存在。")

    stored_answer = (
        db.query(PracticeAnswer)
        .filter(
            PracticeAnswer.session_id == session.id,
            PracticeAnswer.question_id == question_id,
        )
        .first()
    )

    normalized_user = _normalize_answer(user_answer)
    normalized_correct = _normalize_answer(question.answer)
    is_correct = normalized_user.lower() == normalized_correct.lower()

    was_correct = stored_answer.is_correct if stored_answer else None
    if stored_answer is None:
        stored_answer = PracticeAnswer(
            session_id=session.id,
            question_id=question_id,
            user_answer=normalized_user,
            is_correct=is_correct,
        )
        db.add(stored_answer)
    else:
        stored_answer.user_answer = normalized_user
        stored_answer.is_correct = is_correct
        stored_answer.answer_time = datetime.utcnow()

    _update_question_stats(question, was_correct, is_correct)
    _update_session_stats(session, was_correct, is_correct)
    _upsert_wrong_question(db, user_id, question_id, is_correct)

    db.commit()
    db.refresh(stored_answer)
    db.refresh(question)
    db.refresh(session)

    return stored_answer, question, session


def finish_session(
    db: Session,
    user_id: int,
    session_id: int,
) -> PracticeSession:
    """结束练习会话并返回最新状态."""
    session = (
        db.query(PracticeSession)
        .filter(
            PracticeSession.id == session_id,
            PracticeSession.user_id == user_id,
        )
        .first()
    )
    if session is None:
        raise LookupError("练习会话不存在。")

    now = datetime.utcnow()
    session.end_time = now
    if session.start_time:
        session.duration_seconds = int((now - session.start_time).total_seconds())

    correct_count = (
        db.query(PracticeAnswer)
        .filter(PracticeAnswer.session_id == session.id, PracticeAnswer.is_correct.is_(True))
        .count()
    )
    session.correct_count = correct_count

    db.commit()
    db.refresh(session)
    return session


def get_session_result(
    db: Session,
    user_id: int,
    session_id: int,
) -> Tuple[PracticeSession, List[Dict[str, object]]]:
    """获取练习会话的答题详情."""
    session = (
        db.query(PracticeSession)
        .filter(
            PracticeSession.id == session_id,
            PracticeSession.user_id == user_id,
        )
        .first()
    )
    if session is None:
        raise LookupError("练习会话不存在。")

    question_ids: List[int] = list(session.question_ids or [])
    if not question_ids:
        return session, []

    questions = (
        db.query(Question)
        .filter(
            Question.user_id == user_id,
            Question.id.in_(question_ids),
        )
        .all()
    )
    question_map: Dict[int, Question] = {question.id: question for question in questions}

    answers = (
        db.query(PracticeAnswer)
        .filter(PracticeAnswer.session_id == session.id)
        .all()
    )
    answer_map: Dict[int, PracticeAnswer] = {
        answer.question_id: answer for answer in answers
    }

    details: List[Dict[str, object]] = []
    for question_id in question_ids:
        question = question_map.get(question_id)
        if question is None:
            continue

        answer = answer_map.get(question_id)
        user_answer = answer.user_answer if answer else None
        is_correct = bool(answer.is_correct) if answer else False

        details.append(
            {
                "question_id": question.id,
                "question": question.question,
                "question_type": question.question_type,
                "options": question.options or [],
                "user_answer": user_answer,
                "correct_answer": question.answer,
                "is_correct": is_correct,
                "explanation": question.explanation,
            }
        )

    return session, details


def list_history(
    db: Session,
    user_id: int,
    page: int,
    page_size: int,
    mode: str | None = None,
) -> Tuple[int, List[PracticeSession]]:
    """获取练习历史记录."""
    current_page = max(page, 1)
    current_page_size = max(1, min(page_size, MAX_HISTORY_PAGE_SIZE))

    query = db.query(PracticeSession).filter(PracticeSession.user_id == user_id)
    if mode:
        query = query.filter(PracticeSession.mode == mode)

    total = query.count()
    records = (
        query.order_by(PracticeSession.start_time.desc())
        .offset((current_page - 1) * current_page_size)
        .limit(current_page_size)
        .all()
    )
    return total, records
