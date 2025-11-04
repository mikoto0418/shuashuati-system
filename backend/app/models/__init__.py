"""
模型模块初始化
"""
from app.models.user import User, UserSettings  # noqa: F401
from app.models.category import Category  # noqa: F401
from app.models.question import Question  # noqa: F401
from app.models.practice import PracticeSession, PracticeAnswer  # noqa: F401
from app.models.favorite import Favorite, WrongQuestion  # noqa: F401
from app.models.ai_task import AITask  # noqa: F401
from app.models.import_batch import ImportBatch, ImportBatchItem  # noqa: F401
