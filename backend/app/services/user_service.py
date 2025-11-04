"""
用户设置相关服务。
"""
from __future__ import annotations

from sqlalchemy.orm import Session

from app.core.security import encrypt_api_key, get_password_hash, verify_password
from app.models.user import User, UserSettings
from app.schemas.user import (
    UserAISettingsUpdate,
    UserSettingsPreferencesUpdate,
    UserUpdate,
    UserPasswordUpdate,
)


def _ensure_settings(db: Session, user_id: int) -> UserSettings:
    """获取或初始化用户设置记录。"""
    settings = (
        db.query(UserSettings).filter(UserSettings.user_id == user_id).first()
    )
    if settings is None:
        settings = UserSettings(user_id=user_id)
        db.add(settings)
        db.commit()
        db.refresh(settings)
    return settings


def get_user_settings(db: Session, user_id: int) -> UserSettings:
    """返回用户设置。"""
    return _ensure_settings(db, user_id)


def update_user_preferences(
    db: Session, user_id: int, payload: UserSettingsPreferencesUpdate
) -> UserSettings:
    """更新练习偏好设置。"""
    settings = _ensure_settings(db, user_id)

    if payload.practice_mode is not None:
        settings.practice_mode = payload.practice_mode
    if payload.answer_display_mode is not None:
        settings.answer_display_mode = payload.answer_display_mode

    db.commit()
    db.refresh(settings)
    return settings


def update_user_ai_settings(
    db: Session, user_id: int, payload: UserAISettingsUpdate
) -> UserSettings:
    """更新 AI 服务配置。"""
    settings = _ensure_settings(db, user_id)

    if payload.ai_provider is not None:
        settings.ai_provider = payload.ai_provider
    if payload.ai_model is not None:
        settings.ai_model = payload.ai_model

    if payload.api_key is not None:
        settings.encrypted_api_key = (
            encrypt_api_key(payload.api_key)
            if payload.api_key
            else None
        )

    db.commit()
    db.refresh(settings)
    return settings


def update_user_profile(
    db: Session, user: User, payload: UserUpdate
) -> User:
    """更新用户昵称与头像。"""
    if payload.nickname is not None:
        user.nickname = payload.nickname
    if payload.avatar_url is not None:
        user.avatar_url = payload.avatar_url

    db.commit()
    db.refresh(user)
    return user


def change_user_password(
    db: Session, user: User, payload: UserPasswordUpdate
) -> None:
    """修改用户密码。"""
    if not verify_password(payload.old_password, user.hashed_password):
        raise ValueError("原密码不正确")

    user.hashed_password = get_password_hash(payload.new_password)
    db.commit()
    db.refresh(user)
