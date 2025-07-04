from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
import json
from utils.crypto import crypto_manager

db = SQLAlchemy()

class User(db.Model):
    """用户模型"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=True)
    nickname = db.Column(db.String(50), nullable=True)  # 昵称
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), default='user')  # admin, user
    is_active = db.Column(db.Boolean, default=True)
    
    # API配置字段
    ai_model = db.Column(db.String(50), default='gpt-3.5-turbo')
    api_key = db.Column(db.Text, nullable=True)  # 加密存储
    api_base_url = db.Column(db.String(255), nullable=True)
    max_tokens = db.Column(db.Integer, default=1000)
    temperature = db.Column(db.Float, default=0.7)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def set_password(self, password):
        """设置密码"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """检查密码"""
        return check_password_hash(self.password_hash, password)
    
    def set_api_key(self, api_key):
        """安全设置API密钥"""
        if api_key:
            # 验证API密钥格式
            if not crypto_manager.validate_api_key_format(api_key):
                raise ValueError("API密钥格式不正确")
            # 加密存储
            self.api_key = crypto_manager.encrypt_api_key(api_key, self.id)
        else:
            self.api_key = None
    
    def get_api_key(self):
        """安全获取API密钥"""
        if self.api_key:
            try:
                return crypto_manager.decrypt_api_key(self.api_key, self.id)
            except ValueError:
                # 解密失败，可能是旧格式或损坏的数据
                return None
        return None
    
    def get_masked_api_key(self, show_length=8):
        """获取遮蔽的API密钥用于显示"""
        original_key = self.get_api_key()
        if original_key:
            return crypto_manager.mask_api_key(original_key, show_length)
        return ''
    
    def has_valid_api_key(self):
        """检查是否有有效的API密钥"""
        return bool(self.get_api_key())
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'nickname': self.nickname,
            'role': self.role,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def get_api_config(self):
        """获取API配置（不包含敏感信息）"""
        return {
            'ai_model': self.ai_model,
            'api_base_url': self.api_base_url,
            'max_tokens': self.max_tokens,
            'temperature': self.temperature,
            'has_api_key': self.has_valid_api_key(),  # 检查是否有有效的API密钥
            'masked_api_key': self.get_masked_api_key()  # 返回遮蔽的API密钥用于显示
        }

class ProcessingLog(db.Model):
    """AI处理日志模型"""
    __tablename__ = 'processing_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    upload_record_id = db.Column(db.Integer, db.ForeignKey('upload_records.id'), nullable=False)
    step_name = db.Column(db.String(100), nullable=False)  # 处理步骤名称
    step_type = db.Column(db.String(50), nullable=False)  # 步骤类型：parsing, ai_thinking, extraction, validation
    status = db.Column(db.String(20), nullable=False)  # started, completed, failed
    message = db.Column(db.Text, nullable=True)  # 详细信息
    ai_reasoning = db.Column(db.Text, nullable=True)  # AI推理过程
    input_data = db.Column(db.Text, nullable=True)  # 输入数据摘要
    output_data = db.Column(db.Text, nullable=True)  # 输出数据摘要
    duration_ms = db.Column(db.Integer, nullable=True)  # 处理耗时（毫秒）
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # 关系
    upload_record = db.relationship('UploadRecord', backref='processing_logs')
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'upload_record_id': self.upload_record_id,
            'step_name': self.step_name,
            'step_type': self.step_type,
            'status': self.status,
            'message': self.message,
            'ai_reasoning': self.ai_reasoning,
            'input_data': self.input_data,
            'output_data': self.output_data,
            'duration_ms': self.duration_ms,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class Category(db.Model):
    """分类模型"""
    __tablename__ = 'categories'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)  # 默认分类可以没有用户
    sort_order = db.Column(db.Integer, default=0)  # 排序字段
    is_default = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    user = db.relationship('User', backref='categories')
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'user_id': self.user_id,
            'sort_order': self.sort_order,
            'is_default': self.is_default,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class Question(db.Model):
    """题目模型"""
    __tablename__ = 'questions'
    
    id = db.Column(db.Integer, primary_key=True)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    type = db.Column(db.String(20), nullable=False)  # single_choice, multiple_choice, true_false, fill_blank
    content = db.Column(db.Text, nullable=False)  # 题目文本
    options = db.Column(db.Text, nullable=True)  # JSON格式的选项
    answer = db.Column(db.Text, nullable=False)  # 正确答案(JSON格式)
    explanation = db.Column(db.Text, nullable=True)  # 题目解析
    difficulty = db.Column(db.Integer, default=1)  # 难度等级 1-5
    source_file = db.Column(db.String(255), nullable=True)  # 来源文件名
    tags = db.Column(db.Text, nullable=True)  # 题目标签(JSON格式)
    is_active = db.Column(db.Boolean, default=True)  # 是否启用
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    category = db.relationship('Category', backref='questions')
    user = db.relationship('User', backref='questions')
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'category_id': self.category_id,
            'user_id': self.user_id,
            'type': self.type,
            'content': self.content,
            'options': json.loads(self.options) if self.options else None,
            'answer': json.loads(self.answer) if self.answer else None,
            'explanation': self.explanation,
            'difficulty': self.difficulty,
            'source_file': self.source_file,
            'tags': json.loads(self.tags) if self.tags else None,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class PracticeRecord(db.Model):
    """练习记录模型"""
    __tablename__ = 'practice_records'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    question_id = db.Column(db.Integer, db.ForeignKey('questions.id'), nullable=False)
    session_id = db.Column(db.String(100), nullable=True)  # 练习会话ID
    user_answer = db.Column(db.Text, nullable=False)  # 用户作答(JSON格式)
    is_correct = db.Column(db.Boolean, nullable=False)  # 是否答对
    duration_seconds = db.Column(db.Integer, nullable=True)  # 作答用时
    practice_mode = db.Column(db.String(20), default='practice')  # practice, review
    practiced_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # 关系
    user = db.relationship('User', backref='practice_records')
    question = db.relationship('Question', backref='practice_records')
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'question_id': self.question_id,
            'session_id': self.session_id,
            'user_answer': json.loads(self.user_answer) if self.user_answer else None,
            'is_correct': self.is_correct,
            'duration_seconds': self.duration_seconds,
            'practice_mode': self.practice_mode,
            'practiced_at': self.practiced_at.isoformat() if self.practiced_at else None
        }

class WrongAnswer(db.Model):
    """错题本模型"""
    __tablename__ = 'wrong_answers'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    question_id = db.Column(db.Integer, db.ForeignKey('questions.id'), nullable=False)
    error_count = db.Column(db.Integer, default=1)  # 错误次数
    last_error_at = db.Column(db.DateTime, default=datetime.utcnow)  # 最后错误时间
    is_mastered = db.Column(db.Boolean, default=False)  # 是否已掌握
    added_at = db.Column(db.DateTime, default=datetime.utcnow)  # 加入错题本时间
    
    # 关系
    user = db.relationship('User', backref='wrong_answers')
    question = db.relationship('Question', backref='wrong_answers')
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'question_id': self.question_id,
            'error_count': self.error_count,
            'last_error_at': self.last_error_at.isoformat() if self.last_error_at else None,
            'is_mastered': self.is_mastered,
            'added_at': self.added_at.isoformat() if self.added_at else None
        }

class Favorite(db.Model):
    """收藏夹模型"""
    __tablename__ = 'favorites'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    question_id = db.Column(db.Integer, db.ForeignKey('questions.id'), nullable=False)
    notes = db.Column(db.Text, nullable=True)  # 收藏备注
    added_at = db.Column(db.DateTime, default=datetime.utcnow)  # 加入收藏夹时间
    
    # 关系
    user = db.relationship('User', backref='favorites')
    question = db.relationship('Question', backref='favorites')
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'question_id': self.question_id,
            'notes': self.notes,
            'added_at': self.added_at.isoformat() if self.added_at else None
        }

class UploadRecord(db.Model):
    """文件上传记录模型"""
    __tablename__ = 'upload_records'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    original_filename = db.Column(db.String(255), nullable=False)  # 原始文件名
    stored_filename = db.Column(db.String(255), nullable=False)  # 存储的文件名
    file_path = db.Column(db.String(500), nullable=False)  # 存储路径
    file_size = db.Column(db.Integer, nullable=False)  # 文件大小
    file_type = db.Column(db.String(50), nullable=False)  # 文件类型
    mime_type = db.Column(db.String(100), nullable=True)  # MIME类型
    status = db.Column(db.String(20), default='pending')  # uploaded, processing, completed, failed
    extracted_count = db.Column(db.Integer, default=0)  # 提取题目数量
    saved_count = db.Column(db.Integer, default=0)  # 保存到题库的题目数量
    error_message = db.Column(db.Text, nullable=True)  # 错误信息
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)  # 上传时间
    processing_started_at = db.Column(db.DateTime, nullable=True)  # 处理开始时间
    processed_at = db.Column(db.DateTime, nullable=True)  # 处理完成时间
    
    # 新增配置字段
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=True)  # 目标分类
    parse_mode = db.Column(db.String(20), default='ai')  # 解析模式
    question_types = db.Column(db.Text, nullable=True)  # 题目类型（逗号分隔）
    include_answers = db.Column(db.Boolean, default=False)  # 是否包含答案
    include_explanations = db.Column(db.Boolean, default=False)  # 是否包含解析
    enable_split = db.Column(db.Boolean, default=False)  # 是否启用文件分割
    max_chunk_size = db.Column(db.Integer, default=3000)  # 最大分块大小
    
    # 关系
    user = db.relationship('User', backref='upload_records')
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'original_filename': self.original_filename,
            'stored_filename': self.stored_filename,
            'file_path': self.file_path,
            'file_size': self.file_size,
            'file_type': self.file_type,
            'mime_type': self.mime_type,
            'status': self.status,
            'extracted_count': self.extracted_count,
            'saved_count': self.saved_count,
            'error_message': self.error_message,
            'uploaded_at': self.uploaded_at.isoformat() if self.uploaded_at else None,
            'processing_started_at': self.processing_started_at.isoformat() if self.processing_started_at else None,
            'processed_at': self.processed_at.isoformat() if self.processed_at else None,
            'category_id': self.category_id,
            'parse_mode': self.parse_mode,
            'question_types': self.question_types,
            'include_answers': self.include_answers,
            'include_explanations': self.include_explanations,
            'enable_split': self.enable_split,
            'max_chunk_size': self.max_chunk_size
        }