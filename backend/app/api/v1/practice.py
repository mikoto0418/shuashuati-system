"""练习相关路由."""
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_active_user, get_db
from app.models.user import User
from app.schemas.common import PaginatedResponse
from app.schemas.practice import (
    PracticeAnswerDetail,
    PracticeAnswerRequest,
    PracticeAnswerResponse,
    PracticeFinishResponse,
    PracticeHistoryItem,
    PracticeQuestionItem,
    PracticeResultResponse,
    PracticeStartRequest,
    PracticeStartResponse,
    PracticePreviewResponse,
)
from app.services import practice_service

router = APIRouter(prefix="/api/v1/practice", tags=["Practice"])


def _to_question_item(question) -> PracticeQuestionItem:
    return PracticeQuestionItem(
        id=question.id,
        question=question.question,
        question_type=question.question_type,
        options=question.options or [],
        image_url=question.image_url,
    )


@router.post("/preview", response_model=PracticePreviewResponse)
async def preview_practice(
    payload: PracticeStartRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> PracticePreviewResponse:
    total, questions = practice_service.preview_questions(
        db=db,
        user_id=current_user.id,
        mode=payload.mode,
        category_ids=payload.category_ids,
        question_types=payload.question_types,
    )
    items = [_to_question_item(question) for question in questions]
    return PracticePreviewResponse(total_count=total, questions=items)


@router.post("/start", response_model=PracticeStartResponse)
async def start_practice(
    payload: PracticeStartRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> PracticeStartResponse:
    try:
        result = practice_service.start_session(
            db=db,
            user_id=current_user.id,
            mode=payload.mode,
            category_ids=payload.category_ids,
            question_types=payload.question_types,
            question_ids=payload.question_ids,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)
        ) from exc

    items = [_to_question_item(question) for question in result.questions]
    session = result.session
    return PracticeStartResponse(
        session_id=session.id,
        total_count=session.total_count,
        mode=session.mode,
        start_time=session.start_time,
        questions=items,
    )


@router.post("/{session_id}/answer", response_model=PracticeAnswerResponse)
async def submit_answer(
    session_id: int,
    payload: PracticeAnswerRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> PracticeAnswerResponse:
    try:
        answer, question, _ = practice_service.submit_answer(
            db=db,
            user_id=current_user.id,
            session_id=session_id,
            question_id=payload.question_id,
            user_answer=payload.user_answer,
        )
    except LookupError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)
        ) from exc
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)
        ) from exc

    return PracticeAnswerResponse(
        question_id=answer.question_id,
        user_answer=answer.user_answer,
        correct_answer=question.answer,
        is_correct=answer.is_correct,
        explanation=question.explanation,
    )


@router.post("/{session_id}/finish", response_model=PracticeFinishResponse)
async def finish_practice(
    session_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> PracticeFinishResponse:
    try:
        session = practice_service.finish_session(
            db=db,
            user_id=current_user.id,
            session_id=session_id,
        )
    except LookupError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)
        ) from exc

    correct_rate = (
        session.correct_count / session.total_count if session.total_count else 0.0
    )

    return PracticeFinishResponse(
        session_id=session.id,
        total_count=session.total_count,
        correct_count=session.correct_count,
        correct_rate=round(correct_rate, 4),
        duration_seconds=session.duration_seconds or 0,
        end_time=session.end_time or session.start_time,
    )


@router.get(
    "/{session_id}/result",
    response_model=PracticeResultResponse,
)
async def get_practice_result(
    session_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> PracticeResultResponse:
    try:
        session, details = practice_service.get_session_result(
            db=db,
            user_id=current_user.id,
            session_id=session_id,
        )
    except LookupError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)
        ) from exc

    answers = [PracticeAnswerDetail(**item) for item in details]
    correct_count = sum(1 for item in answers if item.is_correct)
    total_count = session.total_count or len(answers)
    correct_rate = correct_count / total_count if total_count else 0.0
    return PracticeResultResponse(
        session_id=session.id,
        mode=session.mode,
        total_count=total_count,
        correct_count=correct_count,
        correct_rate=round(correct_rate, 4),
        duration_seconds=session.duration_seconds or 0,
        start_time=session.start_time,
        end_time=session.end_time or session.start_time,
        answers=answers,
    )


@router.get(
    "/history",
    response_model=PaginatedResponse[PracticeHistoryItem],
)
async def list_practice_history(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    mode: Optional[str] = Query(
        None, pattern="^(sequential|random|wrong|favorite)$"
    ),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> PaginatedResponse[PracticeHistoryItem]:
    safe_page_size = min(page_size, practice_service.MAX_HISTORY_PAGE_SIZE)
    total, records = practice_service.list_history(
        db=db,
        user_id=current_user.id,
        page=page,
        page_size=safe_page_size,
        mode=mode,
    )
    items = []
    for record in records:
        total_count = record.total_count or 0
        correct_count = record.correct_count or 0
        correct_rate = correct_count / total_count if total_count else 0.0
        item = PracticeHistoryItem(
            session_id=record.id,
            mode=record.mode,
            total_count=total_count,
            correct_count=correct_count,
            correct_rate=round(correct_rate, 4),
            duration_seconds=record.duration_seconds,
            start_time=record.start_time,
            end_time=record.end_time,
        )
        items.append(item)

    return PaginatedResponse[PracticeHistoryItem](
        total=total,
        page=page,
        page_size=safe_page_size,
        items=items,
    )
