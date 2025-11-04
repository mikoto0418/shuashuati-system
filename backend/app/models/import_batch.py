"""导入批次模型"""
from datetime import datetime

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    JSON,
    String,
    Text,
)
from sqlalchemy.orm import relationship

from app.core.database import Base


class ImportBatch(Base):
    """记录一次题目导入批次."""

    __tablename__ = "import_batches"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    mode = Column(String(20), nullable=False)
    original_name = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    used_ai = Column(Boolean, default=False)
    warnings = Column(JSON, nullable=True)
    stats = Column(JSON, nullable=True)
    total_count = Column(Integer, nullable=False, default=0)
    success_count = Column(Integer, nullable=False, default=0)
    failed_count = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, default=datetime.utcnow)

    items = relationship(
        "ImportBatchItem",
        back_populates="batch",
        cascade="all, delete-orphan",
    )


class ImportBatchItem(Base):
    """记录批次内单题导入结果."""

    __tablename__ = "import_batch_items"

    id = Column(Integer, primary_key=True, index=True)
    batch_id = Column(
        Integer,
        ForeignKey("import_batches.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    index = Column(Integer, nullable=False)
    question = Column(Text, nullable=False)
    question_type = Column(String(20), nullable=False)
    answer = Column(Text, nullable=True)
    status = Column(String(20), nullable=False)  # success / failed
    message = Column(Text, nullable=True)
    question_id = Column(Integer, ForeignKey("questions.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    batch = relationship("ImportBatch", back_populates="items")
