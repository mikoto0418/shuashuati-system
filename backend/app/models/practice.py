"""
练习模型
"""
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base


class PracticeSession(Base):
    """练习会话表"""
    __tablename__ = "practice_sessions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    mode = Column(String(20), nullable=False)
    category_ids = Column(JSON, nullable=True)
    question_types = Column(JSON, nullable=True)
    question_ids = Column(JSON, nullable=False, default=list)
    total_count = Column(Integer, nullable=False)
    correct_count = Column(Integer, default=0)
    start_time = Column(DateTime, nullable=False, index=True)
    end_time = Column(DateTime, nullable=True)
    duration_seconds = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # 关系
    user = relationship("User", back_populates="practice_sessions")
    answers = relationship("PracticeAnswer", back_populates="session", cascade="all, delete-orphan")


class PracticeAnswer(Base):
    """练习答题记录表"""
    __tablename__ = "practice_answers"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("practice_sessions.id", ondelete="CASCADE"), nullable=False, index=True)
    question_id = Column(Integer, ForeignKey("questions.id", ondelete="CASCADE"), nullable=False, index=True)
    user_answer = Column(Text, nullable=True)
    is_correct = Column(Boolean, nullable=False)
    answer_time = Column(DateTime, default=datetime.utcnow)

    # 关系
    session = relationship("PracticeSession", back_populates="answers")
    question = relationship("Question", back_populates="practice_answers")
