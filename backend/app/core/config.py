"""
配置模块
"""
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """应用配置"""

    # 应用基础配置
    APP_NAME: str = "刷刷题系统"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True

    # 数据库配置
    DATABASE_URL: str = "sqlite:///./shuashuati.db"
    # 生产环境使用 PostgreSQL：
    # DATABASE_URL: str = "postgresql://user:password@localhost/shuashuati_db"

    # JWT 配置
    SECRET_KEY: str = "your-secret-key-change-this-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_DAYS: int = 7

    # AES 加密配置（用于加密 API Key）
    AES_KEY: str = "your-aes-key-32-bytes-change-it"  # 必须是 32 字节

    # 文件上传配置
    MAX_FILE_SIZE: int = 50 * 1024 * 1024  # 50MB
    ALLOWED_EXTENSIONS: set = {".txt", ".docx", ".doc", ".pdf", ".jpg", ".jpeg", ".png", ".bmp"}
    UPLOAD_DIR: str = "./static/uploads"
    IMAGE_DIR: str = "./static/images/questions"
    IMAGE_ALLOWED_EXTENSIONS: set = {".jpg", ".jpeg", ".png", ".bmp"}
    MAX_IMAGE_SIZE: int = 5 * 1024 * 1024  # 5MB

    # CORS 配置
    CORS_ORIGINS: list = ["http://localhost:5173", "http://localhost:3000"]

    # AI 配置
    DEFAULT_AI_PROVIDER: str = "openai"
    DEFAULT_AI_MODEL: str = "gpt-3.5-turbo"


    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
