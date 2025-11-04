"""文件上传与导入相关 Schemas"""
from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from app.schemas.question import QuestionImportItemResult
class ParsedOptionSchema(BaseModel):
    key: str = Field(..., description="选项代号，例如 A/B/C")
    content: str = Field(..., description="选项内容")


class ParsedQuestionSchema(BaseModel):
    index: int
    question: str
    question_type: str
    options: List[ParsedOptionSchema] = []
    answer: str = ""
    explanation: str = ""
    raw_text: str = ""
    tags: List[str] = Field(default_factory=list, description="AI 总结的知识点标签")


class FilePreviewResponse(BaseModel):
    file_path: str
    original_name: str
    text: str
    questions: List[ParsedQuestionSchema]
    mode: str
    used_ai: bool
    warnings: List[str] = Field(default_factory=list)
    stats: Optional[Dict[str, Any]] = None
    events: List[Dict[str, Any]] = Field(default_factory=list)
    auto_imported: bool = False
    import_summary: Optional[Dict[str, Any]] = None


class FileImportRequest(BaseModel):
    file_path: str
    category_id: Optional[int] = None
    questions: List[ParsedQuestionSchema]
    mode: str = "basic"
    original_name: Optional[str] = None
    used_ai: bool = False
    warnings: List[str] = Field(default_factory=list)
    stats: Optional[Dict[str, Any]] = None


class FileImportResult(BaseModel):
    success_count: int
    failed_count: int
    created_ids: List[int]
    errors: List[str] = []
    items: List[QuestionImportItemResult] = []


class ImportBatchSummary(BaseModel):
    id: int
    mode: str
    original_name: str
    used_ai: bool
    total_count: int
    success_count: int
    failed_count: int
    warnings: List[str] = Field(default_factory=list)
    stats: Optional[Dict[str, Any]] = None
    file_path: str
    created_at: datetime
    completed_at: datetime


class ImportBatchItem(BaseModel):
    id: int
    index: int
    question: str
    question_type: str
    answer: str
    status: str
    message: Optional[str] = None
    question_id: Optional[int] = None
    created_at: datetime


class ImportBatchDetail(ImportBatchSummary):
    items: List[ImportBatchItem]


class ImportBatchListResponse(BaseModel):
    batches: List[ImportBatchSummary]
