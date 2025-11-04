"""
Schemas 模块初始化
"""
from app.schemas.user import (
    UserRegister,
    UserLogin,
    UserUpdate,
    UserPasswordUpdate,
    UserResponse,
    UserSettingsPreferencesUpdate,
    UserAISettingsUpdate,
    UserAIModelListRequest,
    UserAIModelListResponse,
    UserSettingsResponse,
    Token,
)
from app.schemas.question import (
    CategoryCreate,
    CategoryUpdate,
    CategoryResponse,
    QuestionCreate,
    QuestionUpdate,
    QuestionResponse,
    QuestionListItem,
    QuestionBatchCreate,
    QuestionBatchCreateResponse,
    QuestionBatchDeleteRequest,
)
from app.schemas.practice import (
    PracticeStartRequest,
    PracticeStartResponse,
    PracticeAnswerRequest,
    PracticeAnswerResponse,
    PracticeFinishResponse,
    PracticeResultResponse,
    PracticeHistoryItem,
)
from app.schemas.common import ResponseModel, PaginatedResponse, MessageResponse
from app.schemas.file import (
    ParsedOptionSchema,
    ParsedQuestionSchema,
    FilePreviewResponse,
    FileImportRequest,
)
from app.schemas.dashboard import DashboardStatsResponse
from app.schemas.ai_task import (
    AITaskCreateResponse,
    AITaskStatusResponse,
    AITaskResult,
    AITaskListResponse,
)

__all__ = [
    # User
    "UserRegister",
    "UserLogin",
    "UserUpdate",
    "UserPasswordUpdate",
    "UserResponse",
    "UserSettingsPreferencesUpdate",
    "UserAISettingsUpdate",
    "UserAIModelListRequest",
    "UserAIModelListResponse",
    "UserSettingsResponse",
    "Token",
    # Question
    "CategoryCreate",
    "CategoryUpdate",
    "CategoryResponse",
    "QuestionCreate",
    "QuestionUpdate",
    "QuestionResponse",
    "QuestionListItem",
    "QuestionBatchCreate",
    "QuestionBatchCreateResponse",
    "QuestionBatchDeleteRequest",
    # Practice
    "PracticeStartRequest",
    "PracticeStartResponse",
    "PracticeAnswerRequest",
    "PracticeAnswerResponse",
    "PracticeFinishResponse",
    "PracticeResultResponse",
    "PracticeHistoryItem",
    # Common
    "ResponseModel",
    "PaginatedResponse",
    "MessageResponse",
    # File
    "ParsedOptionSchema",
    "ParsedQuestionSchema",
    "FilePreviewResponse",
    "FileImportRequest",
    # AI Task
    "AITaskCreateResponse",
    "AITaskStatusResponse",
    "AITaskResult",
    "AITaskListResponse",
    # Dashboard
    "DashboardStatsResponse",
]
