"""
认证服务
"""
from typing import Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.core.security import get_password_hash, verify_password, create_access_token
from app.models.user import User, UserSettings
from app.schemas.user import UserRegister
from datetime import timedelta
from app.core.config import settings


def get_user_by_username(db: Session, username: str) -> Optional[User]:
    """根据用户名查询用户"""
    return db.query(User).filter(User.username == username).first()


def get_user_by_email(db: Session, email: str) -> Optional[User]:
    """根据邮箱查询用户"""
    return db.query(User).filter(User.email == email).first()


def create_user(db: Session, user_in: UserRegister) -> User:
    """创建新用户"""
    if get_user_by_username(db, user_in.username):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户名已存在"
        )

    if get_user_by_email(db, user_in.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="邮箱已被注册"
        )

    has_admin = db.query(User).filter(User.is_admin == True).first() is not None  # noqa: E712

    user = User(
        username=user_in.username,
        email=user_in.email,
        hashed_password=get_password_hash(user_in.password),
        nickname=user_in.nickname
    )
    db.add(user)
    db.flush()

    if not has_admin:
        user.is_admin = True

    settings_record = UserSettings(user_id=user.id)
    db.add(settings_record)

    db.commit()
    db.refresh(user)
    return user


def authenticate_user(db: Session, identifier: str, password: str) -> Optional[User]:
    """验证用户凭据，identifier 支持用户名或邮箱"""
    user = get_user_by_username(db, identifier)
    if user is None and "@" in identifier:
        user = get_user_by_email(db, identifier)

    if user is None:
        return None

    if not verify_password(password, user.hashed_password):
        return None

    return user


def generate_access_token(user_id: int) -> str:
    """为用户生成访问令牌"""
    expires = timedelta(days=settings.ACCESS_TOKEN_EXPIRE_DAYS)
    return create_access_token({"sub": str(user_id)}, expires_delta=expires)
