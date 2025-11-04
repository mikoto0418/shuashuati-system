"""
题目模型
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base


class Question(Base):
    """题目表"""
    __tablename__ = "questions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    category_id = Column(Integer, ForeignKey("categories.id", ondelete="SET NULL"), nullable=True, index=True)
    question = Column(Text, nullable=False)
    question_type = Column(String(20), nullable=False, index=True)
    options = Column(JSON, nullable=True)  # SQLite 会存储为 TEXT
    answer = Column(Text, nullable=False)
    explanation = Column(Text, nullable=True)
    image_url = Column(String(255), nullable=True)
    tags = Column(JSON, nullable=True)
    source_file = Column(String(255), nullable=True)
    practice_count = Column(Integer, default=0)
    correct_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 关系
    user = relationship("User", back_populates="questions")
    category = relationship("Category", back_populates="questions")
    practice_answers = relationship("PracticeAnswer", back_populates="question", cascade="all, delete-orphan")
    favorites = relationship("Favorite", back_populates="question", cascade="all, delete-orphan")
    wrong_records = relationship("WrongQuestion", back_populates="question", cascade="all, delete-orphan")
