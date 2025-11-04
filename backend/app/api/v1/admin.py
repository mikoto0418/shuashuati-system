"""管理员工具接口。"""
from __future__ import annotations

from datetime import datetime, timedelta
from pathlib import Path

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_admin_user, get_db
from app.core.config import settings
from app.models.ai_task import AITask, AITaskStatus
from app.models.user import User
from app.schemas.common import MessageResponse

router = APIRouter(prefix="/api/v1/admin", tags=["Admin"])


@router.post("/uploads/cleanup", response_model=MessageResponse)
async def cleanup_uploads_endpoint(
    retention_hours: int = 6,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
) -> MessageResponse:
    """清理上传目录中过期文件。"""
    now = datetime.utcnow()
    retention_delta = timedelta(hours=retention_hours)

    upload_root = Path(settings.UPLOAD_DIR).resolve()
    protected_paths = set()

    tasks = db.query(AITask).all()
    for task in tasks:
        keep = (
            task.status in {AITaskStatus.PENDING.value, AITaskStatus.RUNNING.value}
            or (task.updated_at and now - task.updated_at <= retention_delta)
        )
        for path_str in (task.file_path, task.result_path):
            if not path_str:
                continue
            path = Path(path_str)
            if not path.is_absolute():
                path = Path(path_str).resolve()
            if keep:
                protected_paths.add(path.resolve())

    removed_files = 0
    scanned_files = 0
    if upload_root.exists():
        for file_path in upload_root.rglob("*"):
            if not file_path.is_file():
                continue
            scanned_files += 1
            resolved = file_path.resolve()
            if resolved in protected_paths:
                continue
            try:
                mtime = datetime.utcfromtimestamp(file_path.stat().st_mtime)
            except OSError:
                continue
            if now - mtime <= retention_delta:
                continue
            try:
                file_path.unlink(missing_ok=True)
                removed_files += 1
            except OSError:
                continue

    message = f"已清理 {removed_files} 个文件 (扫描 {scanned_files} 个，保留 {len(protected_paths)} 个保护文件)。"
    return MessageResponse(message=message)
