"""
文件解析任务 API。
"""
from enum import Enum

from fastapi import (
    APIRouter,
    BackgroundTasks,
    Depends,
    File,
    Form,
    HTTPException,
    UploadFile,
)
from sqlalchemy.orm import Session

from app.api.deps import get_current_active_user, get_db
from app.models.user import User
from app.services import parse_task_service
from app.schemas.ai_task import (
    AITaskCreateResponse,
    AITaskStatusResponse,
    AITaskResult,
    AITaskListResponse,
)


router = APIRouter(prefix="/api/v1/parse-task", tags=["ParseTask"])


class TaskParseMode(str, Enum):
    BASIC = "basic"
    AI = "ai"
    MIXED = "mixed"


@router.post("", response_model=AITaskCreateResponse)
async def create_parse_task(
    background_tasks: BackgroundTasks,
    upload_file: UploadFile = File(...),
    mode: TaskParseMode = Form(TaskParseMode.MIXED),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> AITaskCreateResponse:
    task = parse_task_service.create_task(
        db=db,
        user_id=current_user.id,
        upload_file=upload_file,
        mode=mode.value,
        background_tasks=background_tasks,
    )
    return AITaskCreateResponse(
        task_id=task.id,
        original_name=task.original_name,
        file_path=task.file_path,
    )


@router.get("/{task_id}", response_model=AITaskStatusResponse)
async def get_parse_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> AITaskStatusResponse:
    task = parse_task_service.get_task(db, current_user.id, task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="任务不存在或已删除")
    return parse_task_service.to_status_response(task)


@router.get("/{task_id}/result", response_model=AITaskResult)
async def get_parse_task_result(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> AITaskResult:
    result = parse_task_service.load_task_result(db, current_user.id, task_id)
    if result is None:
        raise HTTPException(status_code=404, detail="任务结果不存在")
    return result


@router.get("", response_model=AITaskListResponse)
async def list_parse_tasks(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> AITaskListResponse:
    tasks = parse_task_service.list_tasks(db, current_user.id)
    return AITaskListResponse(
        tasks=[parse_task_service.to_status_response(task) for task in tasks]
    )
