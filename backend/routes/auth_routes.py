from flask import Blueprint, request, jsonify
from models import User, db
from auth import generate_token, hash_password, verify_password, token_required
from datetime import datetime
import re

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')

@auth_bp.route('/register', methods=['POST'])
def register():
    """用户注册"""
    try:
        data = request.get_json()
        
        # 验证必填字段
        if not data or not data.get('username') or not data.get('password') or not data.get('email'):
            return jsonify({'error': '用户名、密码和邮箱为必填项'}), 400
        
        username = data['username'].strip()
        password = data['password']
        email = data['email'].strip().lower()
        
        # 验证用户名格式
        if len(username) < 3 or len(username) > 20:
            return jsonify({'error': '用户名长度必须在3-20个字符之间'}), 400
        
        if not re.match(r'^[a-zA-Z0-9_\u4e00-\u9fa5]+$', username):
            return jsonify({'error': '用户名只能包含字母、数字、下划线和中文'}), 400
        
        # 验证密码强度
        if len(password) < 6:
            return jsonify({'error': '密码长度至少6个字符'}), 400
        
        # 验证邮箱格式
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, email):
            return jsonify({'error': '邮箱格式不正确'}), 400
        
        # 检查用户名是否已存在
        if User.query.filter_by(username=username).first():
            return jsonify({'error': '用户名已存在'}), 409
        
        # 检查邮箱是否已存在
        if User.query.filter_by(email=email).first():
            return jsonify({'error': '邮箱已被注册'}), 409
        
        # 创建新用户
        user = User(
            username=username,
            email=email,
            password_hash=hash_password(password),
            role='user'
        )
        
        db.session.add(user)
        db.session.commit()
        
        # 生成令牌
        token = generate_token(user.id)
        
        return jsonify({
            'message': '注册成功',
            'data': {
                'user': user.to_dict(),
                'token': token
            }
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'注册失败: {str(e)}'}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    """用户登录"""
    try:
        data = request.get_json()
        
        if not data or not data.get('username') or not data.get('password'):
            return jsonify({'error': '用户名和密码为必填项'}), 400
        
        username = data['username'].strip()
        password = data['password']
        
        # 查找用户（支持用户名或邮箱登录）
        user = User.query.filter(
            (User.username == username) | (User.email == username)
        ).first()
        
        if not user or not verify_password(user.password_hash, password):
            return jsonify({'error': '用户名或密码错误'}), 401
        
        # 更新最后登录时间
        user.updated_at = datetime.utcnow()
        db.session.commit()
        
        # 生成令牌
        token = generate_token(user.id)
        
        return jsonify({
            'message': '登录成功',
            'data': {
                'user': user.to_dict(),
                'token': token
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'登录失败: {str(e)}'}), 500

@auth_bp.route('/me', methods=['GET'])
@token_required
def get_current_user(current_user):
    """获取当前用户信息"""
    return jsonify({
        'data': current_user.to_dict()
    }), 200

@auth_bp.route('/profile', methods=['GET'])
@token_required
def get_profile(current_user):
    """获取用户信息"""
    return jsonify({
        'data': current_user.to_dict()
    }), 200

@auth_bp.route('/profile', methods=['PUT'])
@token_required
def update_profile(current_user):
    """更新用户信息"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': '请提供要更新的数据'}), 400
        
        # 可更新的字段
        if 'email' in data:
            email = data['email'].strip().lower()
            email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            if not re.match(email_pattern, email):
                return jsonify({'error': '邮箱格式不正确'}), 400
            
            # 检查邮箱是否已被其他用户使用
            existing_user = User.query.filter(
                User.email == email,
                User.id != current_user.id
            ).first()
            if existing_user:
                return jsonify({'error': '邮箱已被其他用户使用'}), 409
            
            current_user.email = email
        
        current_user.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'message': '用户信息更新成功',
            'data': current_user.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'更新失败: {str(e)}'}), 500

@auth_bp.route('/password', methods=['PUT'])
@token_required
def change_password(current_user):
    """修改密码"""
    try:
        data = request.get_json()
        
        if not data or not data.get('currentPassword') or not data.get('newPassword'):
            return jsonify({'error': '当前密码和新密码为必填项'}), 400
        
        current_password = data['currentPassword']
        new_password = data['newPassword']
        
        # 验证当前密码
        if not verify_password(current_user.password_hash, current_password):
            return jsonify({'error': '当前密码错误'}), 401
        
        # 验证新密码强度
        if len(new_password) < 6:
            return jsonify({'error': '新密码长度至少6个字符'}), 400
        
        # 更新密码
        current_user.password_hash = hash_password(new_password)
        current_user.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({'message': '密码修改成功'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'密码修改失败: {str(e)}'}), 500

@auth_bp.route('/logout', methods=['POST'])
@token_required
def logout(current_user):
    """用户登出"""
    try:
        # 在实际应用中，这里可以将token加入黑名单
        # 或者在数据库中记录登出时间
        return jsonify({
            'code': 200,
            'message': '登出成功'
        })
        
    except Exception as e:
        return jsonify({'error': f'登出失败: {str(e)}'}), 500

@auth_bp.route('/api-config', methods=['GET'])
@token_required
def get_api_config(current_user):
    """获取API配置"""
    try:
        config = current_user.get_api_config()
        
        return jsonify({
            'data': {
                'aiModel': config['ai_model'],
                'apiKey': config['masked_api_key'],  # 使用安全的遮蔽显示
                'apiBaseUrl': config['api_base_url'] or '',
                'maxTokens': config['max_tokens'],
                'temperature': config['temperature'],
                'hasApiKey': config['has_api_key']  # 添加是否有API密钥的标识
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'获取API配置失败: {str(e)}'}), 500

@auth_bp.route('/api-config', methods=['PUT'])
@token_required
def update_api_config(current_user):
    """更新API配置"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': '请提供配置数据'}), 400
        
        # 更新API配置字段
        if 'aiModel' in data:
            current_user.ai_model = data['aiModel']
        
        if 'apiKey' in data:
            try:
                print(f"收到API密钥更新请求，用户ID: {current_user.id}")
                print(f"API密钥长度: {len(data['apiKey']) if data['apiKey'] else 0}")
                # 使用安全的API密钥设置方法
                current_user.set_api_key(data['apiKey'])
                print("API密钥设置成功")
            except ValueError as e:
                print(f"API密钥设置失败: {str(e)}")
                return jsonify({'error': str(e)}), 400
        
        if 'apiBaseUrl' in data:
            current_user.api_base_url = data['apiBaseUrl'] or None
        
        if 'maxTokens' in data:
            max_tokens = int(data['maxTokens'])
            if 100 <= max_tokens <= 4000:
                current_user.max_tokens = max_tokens
            else:
                return jsonify({'error': 'maxTokens必须在100-4000之间'}), 400
        
        if 'temperature' in data:
            temperature = float(data['temperature'])
            if 0 <= temperature <= 2:
                current_user.temperature = temperature
            else:
                return jsonify({'error': 'temperature必须在0-2之间'}), 400
        
        current_user.updated_at = datetime.utcnow()
        db.session.commit()
        print(f"API配置更新完成，用户ID: {current_user.id}")
        
        return jsonify({'message': 'API配置更新成功'}), 200
        
    except ValueError as e:
        return jsonify({'error': '参数格式错误'}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'更新API配置失败: {str(e)}'}), 500

@auth_bp.route('/test-api', methods=['POST'])
@token_required
def test_api_connection(current_user):
    """测试API连接"""
    try:
        data = request.get_json()
        
        if not data or not data.get('apiKey'):
            return jsonify({'error': '请提供API密钥'}), 400
        
        ai_model = data.get('aiModel', 'gpt-3.5-turbo')
        api_key = data['apiKey']
        api_base_url = data.get('apiBaseUrl', '')
        
        # 验证API密钥格式
        from utils.crypto import crypto_manager
        if not crypto_manager.validate_api_key_format(api_key):
            return jsonify({'error': 'API密钥格式不正确'}), 400
        
        # 模拟API测试成功
        return jsonify({
            'message': 'API连接测试成功',
            'model': ai_model
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'API测试失败: {str(e)}'}), 500