"""
安全模块：密码加密、JWT Token、API Key 加密
"""
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from cryptography.fernet import Fernet
from app.core.config import settings
import base64

# 密码加密上下文
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# AES 加密器（用于加密 API Key）
# 注意：生产环境中应该使用环境变量设置 AES_KEY
aes_key = base64.urlsafe_b64encode(settings.AES_KEY.encode()[:32].ljust(32, b'\0'))
fernet = Fernet(aes_key)


# ========== 密码加密 ==========

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证密码"""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """生成密码哈希"""
    return pwd_context.hash(password)


# ========== JWT Token ==========

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """创建访问令牌"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(days=settings.ACCESS_TOKEN_EXPIRE_DAYS)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str) -> Optional[dict]:
    """解码访问令牌"""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError:
        return None


# ========== API Key 加密 ==========

def encrypt_api_key(api_key: str) -> str:
    """加密 API Key"""
    if not api_key:
        return ""
    encrypted = fernet.encrypt(api_key.encode())
    return encrypted.decode()


def decrypt_api_key(encrypted_api_key: str) -> str:
    """解密 API Key"""
    if not encrypted_api_key:
        return ""
    try:
        decrypted = fernet.decrypt(encrypted_api_key.encode())
        return decrypted.decode()
    except Exception:
        return ""
