"""
AI 解析任务模型。
"""
from datetime import datetime

from enum import Enum

from sqlalchemy import Column, DateTime, Integer, String, Text, Float

from app.core.database import Base


class AITaskStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"


class AITask(Base):
    __tablename__ = "ai_parse_tasks"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True, nullable=False)
    file_path = Column(String(500), nullable=False)
    original_name = Column(String(255), nullable=False)
    mode = Column(String(20), nullable=False)
    status = Column(String(20), default=AITaskStatus.PENDING.value, index=True)
    progress = Column(Float, default=0.0)
    result_path = Column(String(500), nullable=True)
    warning_message = Column(Text, nullable=True)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
