"""
认证路由
"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.config import settings
from app.schemas.user import UserRegister, UserResponse, Token
from app.services.auth import (
    create_user,
    authenticate_user,
    generate_access_token
)
from app.api.deps import get_current_active_user
from app.models.user import User

router = APIRouter(prefix="/api/v1/auth", tags=["认证"])


def _to_user_response(user: User) -> UserResponse:
    data = UserResponse.model_validate(user, from_attributes=True)
    data.is_admin = bool(user.is_admin)
    return data


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register_user(user_in: UserRegister, db: Session = Depends(get_db)) -> UserResponse:
    """
    注册新用户
    """
    user = create_user(db, user_in)
    return _to_user_response(user)


@router.post("/login", response_model=Token)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
) -> Token:
    """
    用户登录，返回访问令牌
    """
    user = authenticate_user(db, form_data.username, form_data.password)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = generate_access_token(user.id)
    expires_in = settings.ACCESS_TOKEN_EXPIRE_DAYS * 24 * 60 * 60
    user_data = _to_user_response(user)

    return Token(
        access_token=access_token,
        token_type="bearer",
        expires_in=expires_in,
        user=user_data
    )


@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_active_user)) -> UserResponse:
    """
    获取当前登录用户信息
    """
    return _to_user_response(current_user)
