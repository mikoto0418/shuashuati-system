from cryptography.fernet import Fernet
import os
import base64
from werkzeug.security import generate_password_hash
import hashlib

class CryptoManager:
    """加密管理器 - 用于API密钥的安全存储"""
    
    def __init__(self, secret_key=None):
        """初始化加密管理器
        
        Args:
            secret_key: 主密钥，如果不提供则从环境变量获取
        """
        if secret_key is None:
            # 从环境变量获取主密钥，如果没有则生成一个
            secret_key = os.environ.get('CRYPTO_SECRET_KEY')
            if not secret_key:
                # 生成一个基于应用的固定密钥（生产环境应该使用更安全的方式）
                secret_key = 'shuashuati_crypto_key_2024'
        
        # 使用密钥生成Fernet密钥
        key_hash = hashlib.sha256(secret_key.encode()).digest()
        self.fernet_key = base64.urlsafe_b64encode(key_hash)
        self.cipher = Fernet(self.fernet_key)
    
    def encrypt_api_key(self, api_key, user_id):
        """加密API密钥
        
        Args:
            api_key: 原始API密钥
            user_id: 用户ID，用于增加安全性
            
        Returns:
            str: 加密后的API密钥
        """
        if not api_key:
            return None
        
        try:
            # 添加用户ID作为盐值，确保不同用户的相同密钥加密结果不同
            salted_key = f"{api_key}:{user_id}"
            encrypted_data = self.cipher.encrypt(salted_key.encode())
            return base64.urlsafe_b64encode(encrypted_data).decode()
        except Exception as e:
            raise ValueError(f"API密钥加密失败: {str(e)}")
    
    def decrypt_api_key(self, encrypted_api_key, user_id):
        """解密API密钥
        
        Args:
            encrypted_api_key: 加密的API密钥
            user_id: 用户ID
            
        Returns:
            str: 解密后的API密钥
        """
        if not encrypted_api_key:
            return None
        
        try:
            encrypted_data = base64.urlsafe_b64decode(encrypted_api_key.encode())
            decrypted_data = self.cipher.decrypt(encrypted_data).decode()
            
            # 移除盐值
            if ':' in decrypted_data:
                api_key, stored_user_id = decrypted_data.rsplit(':', 1)
                # 验证用户ID匹配
                if str(stored_user_id) == str(user_id):
                    return api_key
                else:
                    raise ValueError("用户ID不匹配，无法解密API密钥")
            else:
                # 兼容旧格式（没有用户ID盐值）
                return decrypted_data
        except Exception as e:
            raise ValueError(f"API密钥解密失败: {str(e)}")
    
    def mask_api_key(self, api_key, show_length=8):
        """遮蔽API密钥用于显示
        
        Args:
            api_key: 原始API密钥
            show_length: 显示的字符长度
            
        Returns:
            str: 遮蔽后的API密钥
        """
        if not api_key:
            return ''
        
        if len(api_key) <= show_length:
            return '*' * len(api_key)
        
        return api_key[:show_length] + '*' * (len(api_key) - show_length)
    
    def validate_api_key_format(self, api_key):
        """验证API密钥格式
        
        Args:
            api_key: API密钥
            
        Returns:
            bool: 是否有效
        """
        if not api_key:
            return False
        
        # 基本长度检查
        if len(api_key) < 10:
            return False
        
        # 检查是否包含常见的API密钥前缀
        valid_prefixes = ['sk-', 'api-', 'key-']
        if any(api_key.startswith(prefix) for prefix in valid_prefixes):
            return True
        
        # 如果没有前缀，检查是否为纯字母数字组合
        return api_key.replace('-', '').replace('_', '').isalnum()

# 全局加密管理器实例
crypto_manager = CryptoManager()