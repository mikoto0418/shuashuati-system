"""用户设置与个人信息接口。"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import decrypt_api_key

from app.api.deps import get_current_active_user, get_db
from app.models.user import User, UserSettings
from app.schemas.common import MessageResponse
from app.schemas.user import (
    UserAISettingsUpdate,
    UserAIModelListRequest,
    UserAIModelListResponse,
    UserSettingsPreferencesUpdate,
    UserSettingsResponse,
    UserUpdate,
    UserResponse,
    UserPasswordUpdate,
)
import app.services.ai_extractor as ai_extractor
from app.services.user_service import (
    change_user_password,
    get_user_settings,
    update_user_ai_settings,
    update_user_preferences,
    update_user_profile,
)
from app.services.ai_extractor import list_provider_models

router = APIRouter(prefix="/api/v1/user", tags=["User"])


def _settings_to_response(settings: UserSettings) -> UserSettingsResponse:
    """构建设置响应。"""
    return UserSettingsResponse(
        id=settings.id,
        user_id=settings.user_id,
        ai_provider=settings.ai_provider,
        ai_model=settings.ai_model,
        practice_mode=settings.practice_mode,
        answer_display_mode=settings.answer_display_mode,
        has_api_key=bool(settings.encrypted_api_key),
        created_at=settings.created_at,
        updated_at=settings.updated_at,
    )


@router.get("/settings", response_model=UserSettingsResponse)
async def read_user_settings(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> UserSettingsResponse:
    settings = get_user_settings(db, current_user.id)
    return _settings_to_response(settings)


@router.put("/settings", response_model=UserSettingsResponse)
async def update_user_settings(
    payload: UserSettingsPreferencesUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> UserSettingsResponse:
    settings = update_user_preferences(db, current_user.id, payload)
    return _settings_to_response(settings)


@router.put("/settings/ai", response_model=UserSettingsResponse)
async def update_user_ai_settings_endpoint(
    payload: UserAISettingsUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> UserSettingsResponse:
    settings = update_user_ai_settings(db, current_user.id, payload)
    return _settings_to_response(settings)


@router.post("/settings/models", response_model=UserAIModelListResponse)
async def list_user_ai_models(
    payload: UserAIModelListRequest,
    current_user: User = Depends(get_current_active_user),
) -> UserAIModelListResponse:
    api_key = payload.api_key
    if not api_key:
        settings = current_user.settings
        if settings and settings.encrypted_api_key:
            api_key = decrypt_api_key(settings.encrypted_api_key)
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="尚未提供 API Key，请先输入或保存后重试。",
            )

    models = ai_extractor.list_provider_models(payload.provider, api_key)
    return UserAIModelListResponse(models=models)


@router.put("/profile", response_model=UserResponse)
async def update_user_profile_endpoint(
    payload: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> UserResponse:
    user = update_user_profile(db, current_user, payload)
    response = UserResponse.model_validate(user, from_attributes=True)
    response.is_admin = bool(user.is_admin)
    return response


@router.put("/password", response_model=MessageResponse)
async def change_password_endpoint(
    payload: UserPasswordUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> MessageResponse:
    try:
        change_user_password(db, current_user, payload)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc
    return MessageResponse(message="密码修改成功")
