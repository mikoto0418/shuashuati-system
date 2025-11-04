"""
Dashboard 统计响应模型。
"""
from pydantic import BaseModel, Field


class DashboardStatsResponse(BaseModel):
    """仪表盘概览统计。"""

    today_completed: int = Field(ge=0, description="今日完成练习题目数量")
    today_accuracy: float = Field(ge=0.0, le=1.0, description="今日正确率，0-1 之间")
    pending_wrong_questions: int = Field(
        ge=0, description="错题本中等待复习的题目数量"
    )
    total_practice_questions: int = Field(
        ge=0, description="累计完成练习的题目数量"
    )
    total_favorites: int = Field(ge=0, description="收藏题目数量")
    ai_parse_count: int = Field(ge=0, description="使用 AI 解析的导入次数")
