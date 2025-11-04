"""
Dashboard 统计接口。
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_active_user, get_db
from app.models.user import User
from app.schemas.dashboard import DashboardStatsResponse
from app.services import get_dashboard_stats

router = APIRouter(prefix="/api/v1/dashboard", tags=["Dashboard"])


@router.get("/overview", response_model=DashboardStatsResponse)
async def dashboard_overview(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> DashboardStatsResponse:
    stats = get_dashboard_stats(db=db, user_id=current_user.id)
    return DashboardStatsResponse(**stats)
