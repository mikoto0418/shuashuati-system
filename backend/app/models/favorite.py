"""
收藏和错题模型
"""
from sqlalchemy import Column, Integer, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base


class Favorite(Base):
    """收藏表"""
    __tablename__ = "favorites"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    question_id = Column(Integer, ForeignKey("questions.id", ondelete="CASCADE"), nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # 关系
    user = relationship("User", back_populates="favorites")
    question = relationship("Question", back_populates="favorites")

    __table_args__ = (
        UniqueConstraint('user_id', 'question_id', name='uq_user_favorite'),
    )


class WrongQuestion(Base):
    """错题本表"""
    __tablename__ = "wrong_questions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    question_id = Column(Integer, ForeignKey("questions.id", ondelete="CASCADE"), nullable=False, index=True)
    wrong_count = Column(Integer, default=1)
    last_wrong_time = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)

    # 关系
    user = relationship("User", back_populates="wrong_questions")
    question = relationship("Question", back_populates="wrong_records")

    __table_args__ = (
        UniqueConstraint('user_id', 'question_id', name='uq_user_wrong_question'),
    )
