from flask import Flask, jsonify, request, session
from flask_cors import CORS
from flask_migrate import Migrate
import os

# 导入配置和模型
from config import config
from models import db, User, Category, Question, PracticeRecord

# 导入路由蓝图
from routes.auth_routes import auth_bp
from routes.question_routes import question_bp
from routes.category_routes import category_bp
from routes.practice_routes import practice_bp
from routes.collection_routes import collection_bp
from routes.upload_routes import upload_bp
from routes.dashboard_routes import dashboard_bp
from routes.favorites_routes import favorites_bp
from routes.api_routes import api_bp

def create_app(config_name='development'):
    """应用工厂函数"""
    app = Flask(__name__)
    
    # 加载配置
    app.config.from_object(config[config_name])
    
    # 初始化扩展
    db.init_app(app)
    # 配置CORS，允许前端访问
    CORS(app, 
         origins=['http://localhost:3000', 'http://127.0.0.1:3000', 'http://localhost:3001', 'http://127.0.0.1:3001', 'http://localhost:3002', 'http://127.0.0.1:3002'],
         supports_credentials=True,
         allow_headers=['Content-Type', 'Authorization'],
         methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'])
    migrate = Migrate(app, db)
    
    # 注册蓝图
    app.register_blueprint(auth_bp)
    app.register_blueprint(question_bp)
    app.register_blueprint(category_bp)
    app.register_blueprint(practice_bp)
    app.register_blueprint(collection_bp)
    app.register_blueprint(upload_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(favorites_bp)
    app.register_blueprint(api_bp)
    
    # 创建数据库表和初始数据
    with app.app_context():
        db.create_all()
        print("✅ 数据库表创建完成")
        
        # 创建默认分类
        if not Category.query.filter_by(is_default=True).first():
            default_categories = [
                {'name': '数学', 'description': '数学相关题目', 'sort_order': 1},
                {'name': '语文', 'description': '语文相关题目', 'sort_order': 2},
                {'name': '英语', 'description': '英语相关题目', 'sort_order': 3},
                {'name': '物理', 'description': '物理相关题目', 'sort_order': 4},
                {'name': '化学', 'description': '化学相关题目', 'sort_order': 5},
                {'name': '生物', 'description': '生物相关题目', 'sort_order': 6},
                {'name': '历史', 'description': '历史相关题目', 'sort_order': 7},
                {'name': '地理', 'description': '地理相关题目', 'sort_order': 8},
                {'name': '政治', 'description': '政治相关题目', 'sort_order': 9},
                {'name': '其他', 'description': '其他类型题目', 'sort_order': 10, 'is_default': True}
            ]
            
            for cat_data in default_categories:
                category = Category(
                    name=cat_data['name'],
                    description=cat_data['description'],
                    sort_order=cat_data['sort_order'],
                    is_default=cat_data.get('is_default', False)
                )
                db.session.add(category)
            
            db.session.commit()
            print('✅ 默认分类创建完成')
    
    return app

# 创建应用实例
app = create_app()

# 健康检查接口
@app.route('/api/health', methods=['GET'])
def health_check():
    """健康检查接口"""
    return jsonify({
        'status': 'healthy',
        'message': '刷刷题系统后端服务运行正常',
        'version': '1.0.0'
    })

# 基础路由
@app.route('/', methods=['GET'])
def index():
    """根路径"""
    return jsonify({
        'message': '欢迎使用刷刷题系统API',
        'docs': '/api/health'
    })

if __name__ == '__main__':
    print("🚀 启动刷刷题系统后端服务...")
    print("📍 健康检查: http://localhost:5000/api/health")
    app.run(host='0.0.0.0', port=5000, debug=True, use_reloader=False)