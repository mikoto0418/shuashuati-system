"""
AI 解析任务相关 Schemas。
"""
from datetime import datetime
from typing import Optional, List, Dict, Any

from pydantic import BaseModel, Field


class AITaskCreateResponse(BaseModel):
    """创建任务响应"""

    task_id: int
    original_name: str
    file_path: str


class AITaskStatusResponse(BaseModel):
    """任务状态查询响应"""

    id: int
    status: str
    progress: float
    mode: str
    original_name: str
    file_path: str
    warnings: List[str] = Field(default_factory=list)
    error: Optional[str] = None
    stats: Optional[Dict[str, Any]] = None
    events: List[Dict[str, Any]] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime


class AITaskResult(BaseModel):
    """任务完成后的结果"""

    id: int
    status: str
    questions: List[dict]
    warnings: List[str] = Field(default_factory=list)
    original_name: str
    file_path: str
    used_ai: bool = False
    stats: Optional[Dict[str, Any]] = None
    events: List[Dict[str, Any]] = Field(default_factory=list)
    auto_imported: bool = False
    import_summary: Optional[Dict[str, Any]] = None


class AITaskListResponse(BaseModel):
    """任务列表响应"""

    tasks: List[AITaskStatusResponse]
