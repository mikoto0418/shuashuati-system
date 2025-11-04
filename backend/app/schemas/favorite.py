"""Favorite question schemas."""
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel


class FavoriteItem(BaseModel):
    question_id: int
    question: str
    question_type: str
    options: List[str]
    answer: str
    explanation: Optional[str] = None
    created_at: datetime
    category_id: Optional[int] = None
    category_name: Optional[str] = None


class FavoriteCreateRequest(BaseModel):
    question_id: int


class FavoriteResponse(BaseModel):
    question_id: int


class FavoriteListResponse(BaseModel):
    items: List[FavoriteItem]
