"""Wrong question schemas."""
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel


class WrongQuestionItem(BaseModel):
    question_id: int
    question: str
    question_type: str
    options: List[str]
    answer: str
    explanation: Optional[str] = None
    wrong_count: int
    last_wrong_time: datetime
    category_id: Optional[int] = None
    category_name: Optional[str] = None

    class Config:
        from_attributes = True


class WrongQuestionListResponse(BaseModel):
    items: List[WrongQuestionItem]


class RemoveWrongQuestionResponse(BaseModel):
    message: str = "Wrong question removed"
