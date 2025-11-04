"""FastAPI application entrypoint."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy import text

from app.core.config import settings
from app.core.database import Base, engine
from app.models import *  # noqa: F401,F403
from app.api.v1 import router as api_v1_router


def _ensure_sqlite_schema() -> None:
    """补齐 SQLite 环境可能缺失的列，用于兼容旧版数据库。"""
    if "sqlite" not in settings.DATABASE_URL:
        return

    with engine.begin() as connection:
        columns = {
            row[1]
            for row in connection.execute(text("PRAGMA table_info('practice_sessions')"))
        }
        if "question_ids" not in columns:
            connection.execute(
                text("ALTER TABLE practice_sessions ADD COLUMN question_ids JSON")
            )
            connection.execute(
                text("UPDATE practice_sessions SET question_ids = '[]' WHERE question_ids IS NULL")
            )

        user_columns = {
            row[1]
            for row in connection.execute(text("PRAGMA table_info('users')"))
        }
        if "is_admin" not in user_columns:
            connection.execute(
                text("ALTER TABLE users ADD COLUMN is_admin BOOLEAN DEFAULT 0")
            )
            first_admin = connection.execute(
                text("SELECT id FROM users ORDER BY id ASC LIMIT 1")
            ).fetchone()
            if first_admin:
                connection.execute(
                    text("UPDATE users SET is_admin = 1 WHERE id = :id"),
                    {"id": first_admin[0]},
                )


Base.metadata.create_all(bind=engine)
_ensure_sqlite_schema()

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    debug=settings.DEBUG,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/")
async def root() -> dict:
    return {
        "app_name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "message": "Welcome to the Shuashuati API",
    }


@app.get("/health")
async def health_check() -> dict:
    return {"status": "ok"}


app.include_router(api_v1_router)
