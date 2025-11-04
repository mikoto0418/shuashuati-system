"""
Question routes.
"""
from typing import Optional

from fastapi import (
    APIRouter,
    Depends,
    File,
    Form,
    HTTPException,
    Query,
    UploadFile,
    status,
)
from sqlalchemy.orm import Session

from app.api.deps import get_current_active_user, get_db
from app.models.user import User
from app.schemas.common import MessageResponse, PaginatedResponse
from app.schemas.question import (
    QuestionBatchDeleteRequest,
    QuestionCreate,
    QuestionImageUploadResponse,
    QuestionListItem,
    QuestionResponse,
    QuestionUpdate,
)
from app.services import question_service
from app.services.file_service import remove_static_file, store_question_image

router = APIRouter(prefix="/api/v1/question", tags=["Question"])


def _paginate(
    total: int,
    page: int,
    page_size: int,
    items: list[QuestionListItem],
) -> PaginatedResponse[QuestionListItem]:
    return PaginatedResponse[QuestionListItem](
        total=total,
        page=page,
        page_size=page_size,
        items=items,
    )


@router.get("/", response_model=PaginatedResponse[QuestionListItem])
async def list_questions(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    keyword: Optional[str] = Query(None),
    category_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    total, records = question_service.list_questions(
        db=db,
        user_id=current_user.id,
        page=page,
        page_size=page_size,
        keyword=keyword,
        category_id=category_id,
    )
    items = [question_service.to_list_item(record) for record in records]
    return _paginate(total, page, page_size, items)


@router.delete("/batch", response_model=MessageResponse)
async def delete_questions_batch(
    payload: QuestionBatchDeleteRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> MessageResponse:
    deleted = question_service.delete_questions_batch(
        db, current_user.id, payload.ids
    )
    return MessageResponse(message=f"Deleted {deleted} questions")


@router.post(
    "/",
    response_model=QuestionResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_question(
    payload: QuestionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> QuestionResponse:
    try:
        question = question_service.create_question(db, current_user.id, payload)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)
        ) from exc
    return question_service.to_response(question)


@router.put("/{question_id}", response_model=QuestionResponse)
async def update_question(
    question_id: int,
    payload: QuestionUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> QuestionResponse:
    try:
        question = question_service.update_question(
            db, current_user.id, question_id, payload
        )
    except LookupError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)
        ) from exc
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)
        ) from exc
    return question_service.to_response(question)


@router.post("/image", response_model=QuestionImageUploadResponse)
async def upload_question_image(
    upload_file: UploadFile = File(...),
    question_id: Optional[int] = Form(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> QuestionImageUploadResponse:
    target_question_id: Optional[int] = None
    if question_id is not None:
        try:
            # 先确认题目归属，避免产生孤立文件
            question_service.get_question(db, current_user.id, question_id)
            target_question_id = question_id
        except LookupError as exc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)
            ) from exc

    relative_path, public_path = store_question_image(upload_file)
    try:
        if target_question_id is not None:
            question_service.update_question(
                db=db,
                user_id=current_user.id,
                question_id=target_question_id,
                payload=QuestionUpdate(image_url=public_path),
            )
    except LookupError as exc:
        remove_static_file(public_path)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)
        ) from exc

    return QuestionImageUploadResponse(
        image_url=public_path,
        relative_path=relative_path,
        question_id=target_question_id,
    )


@router.delete("/{question_id}", response_model=MessageResponse)
async def delete_question(
    question_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> MessageResponse:
    try:
        question_service.delete_question(db, current_user.id, question_id)
    except LookupError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)
        ) from exc
    return MessageResponse(message="Question deleted")

@router.get("/{question_id}", response_model=QuestionResponse)
async def get_question(
    question_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> QuestionResponse:
    try:
        question = question_service.get_question(db, current_user.id, question_id)
    except LookupError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)
        ) from exc
    return question_service.to_response(question)
