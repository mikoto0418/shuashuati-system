"""
分类和题目相关的 Pydantic Schemas
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


# ========== Category Schemas ==========

class CategoryBase(BaseModel):
    """分类基础模型"""
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    parent_id: Optional[int] = None


class CategoryCreate(CategoryBase):
    """创建分类"""
    pass


class CategoryUpdate(BaseModel):
    """更新分类"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    parent_id: Optional[int] = None


class CategoryResponse(CategoryBase):
    """分类响应"""
    id: int
    user_id: int
    question_count: int = 0
    created_at: datetime
    updated_at: datetime
    children: List['CategoryResponse'] = []

    class Config:
        from_attributes = True


# ========== Question Schemas ==========

class QuestionBase(BaseModel):
    """题目基础模型"""
    question: str = Field(..., min_length=1)
    question_type: str = Field(..., pattern="^(single_choice|multiple_choice|true_false|fill_blank|short_answer)$")
    options: Optional[List[str]] = None
    answer: str = Field(..., min_length=1)
    explanation: Optional[str] = None
    image_url: Optional[str] = None
    tags: Optional[List[str]] = []


class QuestionCreate(QuestionBase):
    """创建题目"""
    category_id: Optional[int] = None
    source_file: Optional[str] = None


class QuestionBatchCreate(BaseModel):
    """批量创建题目"""
    category_id: Optional[int] = None
    questions: List[QuestionCreate]


class QuestionUpdate(BaseModel):
    """更新题目"""
    question: Optional[str] = None
    question_type: Optional[str] = Field(None, pattern="^(single_choice|multiple_choice|true_false|fill_blank|short_answer)$")
    options: Optional[List[str]] = None
    answer: Optional[str] = None
    explanation: Optional[str] = None
    image_url: Optional[str] = None
    tags: Optional[List[str]] = None
    category_id: Optional[int] = None


class QuestionListItem(BaseModel):
    """题目列表项（简化版）"""
    id: int
    question: str
    question_type: str
    answer: str
    category_id: Optional[int] = None
    category_name: Optional[str] = None
    practice_count: int = 0
    correct_count: int = 0
    correct_rate: float = 0.0
    has_image: bool = False
    created_at: datetime

    class Config:
        from_attributes = True


class QuestionResponse(QuestionBase):
    """题目响应（完整版）"""
    id: int
    user_id: int
    category_id: Optional[int] = None
    category_name: Optional[str] = None
    source_file: Optional[str] = None
    practice_count: int = 0
    correct_count: int = 0
    correct_rate: float = 0.0
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class QuestionBatchCreateResponse(BaseModel):
    """批量创建响应"""
    success_count: int
    failed_count: int
    created_ids: List[int]
    errors: List[str] = []
    items: List["QuestionImportItemResult"] = []
    batch_id: Optional[int] = None


class QuestionBatchDeleteRequest(BaseModel):
    """批量删除请求"""
    ids: List[int] = Field(..., min_length=1)


class QuestionImportItemResult(BaseModel):
    """单题导入结果"""

    index: int
    question: str
    question_type: str
    answer: str
    status: str
    message: Optional[str] = None
    question_id: Optional[int] = None
    tags: List[str] = Field(default_factory=list)


QuestionBatchCreateResponse.model_rebuild()


class QuestionImageUploadResponse(BaseModel):
    """题目图片上传响应"""

    image_url: str
    relative_path: str
    question_id: Optional[int] = None
