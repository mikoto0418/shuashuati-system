from functools import wraps
from flask import request, jsonify, current_app
import jwt
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
from models import User, db

def generate_token(user_id):
    """生成JWT令牌"""
    payload = {
        'user_id': user_id,
        'exp': datetime.utcnow() + timedelta(days=7),  # 7天过期
        'iat': datetime.utcnow()
    }
    return jwt.encode(payload, current_app.config['SECRET_KEY'], algorithm='HS256')

def verify_token(token):
    """验证JWT令牌"""
    try:
        payload = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
        return payload['user_id']
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

def token_required(f):
    """装饰器：要求用户登录"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        # 从请求头获取token
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            try:
                token = auth_header.split(' ')[1]  # Bearer <token>
            except IndexError:
                return jsonify({'error': '无效的认证头格式'}), 401
        
        if not token:
            return jsonify({'error': '缺少认证令牌'}), 401
        
        user_id = verify_token(token)
        if user_id is None:
            return jsonify({'error': '无效或过期的令牌'}), 401
        
        # 获取用户信息
        current_user = User.query.get(user_id)
        if not current_user:
            return jsonify({'error': '用户不存在'}), 401
        
        return f(current_user, *args, **kwargs)
    
    return decorated

def admin_required(f):
    """装饰器：要求管理员权限"""
    @wraps(f)
    def decorated(current_user, *args, **kwargs):
        if current_user.role != 'admin':
            return jsonify({'error': '需要管理员权限'}), 403
        return f(current_user, *args, **kwargs)
    
    return decorated

def hash_password(password):
    """密码哈希"""
    return generate_password_hash(password)

def verify_password(password_hash, password):
    """验证密码"""
    return check_password_hash(password_hash, password)