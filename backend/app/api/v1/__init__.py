"""v1 路由包"""

from fastapi import APIRouter

from . import (
    admin,
    auth,
    category,
    dashboard,
    favorite,
    file,
    parse_task,
    practice,
    question,
    user,
    wrong_question,
)

router = APIRouter()

router.include_router(auth.router)
router.include_router(category.router)
router.include_router(favorite.router)
router.include_router(file.router)
router.include_router(dashboard.router)
router.include_router(practice.router)
router.include_router(question.router)
router.include_router(user.router)
router.include_router(wrong_question.router)
router.include_router(parse_task.router)
router.include_router(admin.router)
