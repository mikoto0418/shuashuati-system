"""
用户相关的 Pydantic Schemas
"""
from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional
from datetime import datetime


# ========== User Schemas ==========

class UserBase(BaseModel):
    """用户基础模型"""
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr


class UserRegister(UserBase):
    """用户注册"""
    password: str = Field(..., min_length=8, max_length=50)
    nickname: Optional[str] = Field(None, max_length=50)


class UserLogin(BaseModel):
    """用户登录"""
    username: str
    password: str


class UserUpdate(BaseModel):
    """用户信息更新"""
    nickname: Optional[str] = Field(None, max_length=50)
    avatar_url: Optional[str] = None


class UserPasswordUpdate(BaseModel):
    """密码更新"""
    old_password: str
    new_password: str = Field(..., min_length=8, max_length=50)


class UserResponse(UserBase):
    """用户响应"""
    id: int
    nickname: Optional[str] = None
    avatar_url: Optional[str] = None
    is_active: bool
    created_at: datetime
    is_admin: bool = False

    class Config:
        from_attributes = True


# ========== UserSettings Schemas ==========

class UserSettingsBase(BaseModel):
    """用户设置基础模型"""
    ai_provider: Optional[str] = "openai"
    ai_model: Optional[str] = "gpt-3.5-turbo"
    practice_mode: Optional[str] = "random"
    answer_display_mode: Optional[str] = "immediate"


class UserSettingsPreferencesUpdate(BaseModel):
    """练习偏好更新"""
    practice_mode: Optional[str] = None
    answer_display_mode: Optional[str] = None


class UserAISettingsUpdate(BaseModel):
    """AI 配置更新"""
    ai_provider: Optional[str] = None
    ai_model: Optional[str] = None
    api_key: Optional[str] = None  # 前端传递，后端加密存储


class UserAIModelListRequest(BaseModel):
    """AI 模型列表请求"""
    provider: str
    api_key: Optional[str] = None


class UserAIModelListResponse(BaseModel):
    """AI 模型列表响应"""
    models: List[str]


class UserSettingsResponse(UserSettingsBase):
    """用户设置响应"""
    id: int
    user_id: int
    has_api_key: bool = False  # 不返回实际的 API Key，只返回是否配置
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ========== Token Schemas ==========

class Token(BaseModel):
    """Token 响应"""
    access_token: str
    token_type: str = "bearer"
    expires_in: int = 604800  # 7 天
    user: UserResponse
