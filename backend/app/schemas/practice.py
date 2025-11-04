"""
练习相关的 Pydantic Schemas
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


# ========== Practice Schemas ==========

class PracticeStartRequest(BaseModel):
    """开始练习请求"""
    category_ids: List[int] = Field(default_factory=list)
    question_types: List[str] = Field(default_factory=list)
    mode: str = Field(..., pattern="^(sequential|random|wrong|favorite)$")
    question_ids: Optional[List[int]] = None


class PracticeAnswerRequest(BaseModel):
    """提交答案请求"""
    question_id: int
    user_answer: Optional[str] = None


class PracticeAnswerResponse(BaseModel):
    """提交答案响应"""
    question_id: int
    user_answer: Optional[str] = None
    correct_answer: Optional[str] = None  # 立即显示模式才返回
    is_correct: Optional[bool] = None  # 立即显示模式才返回
    explanation: Optional[str] = None  # 立即显示模式才返回


class PracticeQuestionItem(BaseModel):
    """练习中的题目"""
    id: int
    question: str
    question_type: str
    options: List[str] = Field(default_factory=list)
    image_url: Optional[str] = None

    class Config:
        from_attributes = True


class PracticeStartResponse(BaseModel):
    """开始练习响应"""
    session_id: int
    total_count: int
    mode: str
    start_time: datetime
    questions: List[PracticeQuestionItem]


class PracticePreviewResponse(BaseModel):
    """练习题目预览响应"""

    total_count: int
    questions: List[PracticeQuestionItem]


class PracticeFinishResponse(BaseModel):
    """结束练习响应"""
    session_id: int
    total_count: int
    correct_count: int
    correct_rate: float
    duration_seconds: int
    end_time: datetime


class PracticeAnswerDetail(BaseModel):
    """答题详情"""
    question_id: int
    question: str
    question_type: str
    options: Optional[List[str]] = None
    user_answer: Optional[str] = None
    correct_answer: str
    is_correct: bool
    explanation: Optional[str] = None


class PracticeResultResponse(BaseModel):
    """练习结果响应"""
    session_id: int
    mode: str
    total_count: int
    correct_count: int
    correct_rate: float
    duration_seconds: int
    start_time: datetime
    end_time: datetime
    answers: List[PracticeAnswerDetail]


class PracticeHistoryItem(BaseModel):
    """练习历史项"""
    session_id: int
    mode: str
    total_count: int
    correct_count: int
    correct_rate: float
    duration_seconds: Optional[int] = None
    start_time: datetime
    end_time: Optional[datetime] = None

    class Config:
        from_attributes = True
