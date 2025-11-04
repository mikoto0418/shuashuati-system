"""Favorite routes."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_current_active_user, get_db
from app.models.user import User
from app.schemas.common import MessageResponse
from app.schemas.favorite import FavoriteCreateRequest, FavoriteItem, FavoriteResponse
from app.services import (
    add_favorite,
    favorite_to_dict,
    list_favorites,
    remove_favorite,
)

router = APIRouter(prefix="/api/v1/favorite", tags=["Favorite"])


@router.get("/", response_model=list[FavoriteItem])
async def get_favorites(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> list[FavoriteItem]:
    favorites = list_favorites(db, current_user.id)
    return [FavoriteItem.model_validate(favorite_to_dict(item)) for item in favorites]


@router.post("/", response_model=FavoriteResponse)
async def create_favorite(
    payload: FavoriteCreateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> FavoriteResponse:
    favorite = add_favorite(db, current_user.id, payload.question_id)
    return FavoriteResponse(question_id=favorite.question_id)


@router.delete("/{question_id}", response_model=MessageResponse)
async def delete_favorite(
    question_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> MessageResponse:
    try:
        remove_favorite(db, current_user.id, question_id)
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return MessageResponse(message="Favorite removed")
