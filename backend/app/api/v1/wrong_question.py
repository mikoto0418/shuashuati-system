"""Wrong question routes."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_current_active_user, get_db
from app.models.user import User
from app.schemas.common import MessageResponse
from app.schemas.wrong_question import WrongQuestionItem
from app.services import wrong_question_to_dict
from app.services import list_wrong_questions, delete_wrong_question

router = APIRouter(prefix="/api/v1/wrong-question", tags=["WrongQuestion"])


@router.get("/", response_model=list[WrongQuestionItem])
async def get_wrong_questions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> list[WrongQuestionItem]:
    records = list_wrong_questions(db, current_user.id)
    return [WrongQuestionItem.model_validate(wrong_question_to_dict(record)) for record in records]


@router.delete("/{question_id}", response_model=MessageResponse)
async def remove_wrong_question(
    question_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> MessageResponse:
    try:
        delete_wrong_question(db, current_user.id, question_id)
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return MessageResponse(message="Wrong question removed")
