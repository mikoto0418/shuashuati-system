from flask import Blueprint, request, jsonify
from models import Category, Question, db
from auth import token_required, admin_required
from datetime import datetime

category_bp = Blueprint('categories', __name__, url_prefix='/api/categories')

@category_bp.route('', methods=['GET'])
@token_required
def get_categories(current_user):
    """获取分类列表"""
    try:
        # 获取查询参数
        include_count = request.args.get('include_count', 'false').lower() == 'true'
        
        categories = Category.query.order_by(Category.sort_order.asc(), Category.created_at.asc()).all()
        
        result = []
        for category in categories:
            category_dict = category.to_dict()
            
            # 如果需要包含题目数量
            if include_count:
                question_count = Question.query.filter(
                    Question.category_id == category.id,
                    Question.is_active == True
                ).count()
                category_dict['question_count'] = question_count
            
            result.append(category_dict)
        
        return jsonify({
            'categories': result
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'获取分类列表失败: {str(e)}'}), 500

@category_bp.route('/<int:category_id>', methods=['GET'])
@token_required
def get_category(current_user, category_id):
    """获取单个分类详情"""
    try:
        category = Category.query.get(category_id)
        if not category:
            return jsonify({'error': '分类不存在'}), 404
        
        # 获取该分类下的题目数量
        question_count = Question.query.filter(
            Question.category_id == category_id,
            Question.is_active == True
        ).count()
        
        category_dict = category.to_dict()
        category_dict['question_count'] = question_count
        
        return jsonify({
            'category': category_dict
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'获取分类详情失败: {str(e)}'}), 500

@category_bp.route('', methods=['POST'])
@token_required
@admin_required
def create_category(current_user):
    """创建分类"""
    try:
        data = request.get_json()
        
        # 验证必填字段
        if not data or not data.get('name'):
            return jsonify({'error': '分类名称为必填项'}), 400
        
        name = data['name'].strip()
        
        # 检查分类名称是否已存在
        if Category.query.filter_by(name=name).first():
            return jsonify({'error': '分类名称已存在'}), 409
        
        # 获取排序值
        sort_order = data.get('sort_order', 0)
        if sort_order is None:
            # 如果没有指定排序，设置为最大值+1
            max_sort = db.session.query(db.func.max(Category.sort_order)).scalar() or 0
            sort_order = max_sort + 1
        
        # 创建分类
        category = Category(
            name=name,
            description=data.get('description', '').strip(),
            sort_order=sort_order,
            is_default=data.get('is_default', False)
        )
        
        db.session.add(category)
        db.session.commit()
        
        return jsonify({
            'message': '分类创建成功',
            'category': category.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'创建分类失败: {str(e)}'}), 500

@category_bp.route('/<int:category_id>', methods=['PUT'])
@token_required
@admin_required
def update_category(current_user, category_id):
    """更新分类"""
    try:
        category = Category.query.get(category_id)
        if not category:
            return jsonify({'error': '分类不存在'}), 404
        
        data = request.get_json()
        if not data:
            return jsonify({'error': '请提供要更新的数据'}), 400
        
        # 更新分类名称
        if 'name' in data:
            name = data['name'].strip()
            if not name:
                return jsonify({'error': '分类名称不能为空'}), 400
            
            # 检查名称是否与其他分类重复
            existing_category = Category.query.filter(
                Category.name == name,
                Category.id != category_id
            ).first()
            if existing_category:
                return jsonify({'error': '分类名称已存在'}), 409
            
            category.name = name
        
        # 更新其他字段
        if 'description' in data:
            category.description = data['description'].strip()
        
        if 'sort_order' in data:
            category.sort_order = data['sort_order']
        
        if 'is_default' in data:
            category.is_default = bool(data['is_default'])
        
        category.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'message': '分类更新成功',
            'category': category.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'更新分类失败: {str(e)}'}), 500

@category_bp.route('/<int:category_id>', methods=['DELETE'])
@token_required
@admin_required
def delete_category(current_user, category_id):
    """删除分类"""
    try:
        category = Category.query.get(category_id)
        if not category:
            return jsonify({'error': '分类不存在'}), 404
        
        # 检查是否为默认分类
        if category.is_default:
            return jsonify({'error': '不能删除默认分类'}), 400
        
        # 检查分类下是否有题目
        question_count = Question.query.filter(
            Question.category_id == category_id,
            Question.is_active == True
        ).count()
        
        if question_count > 0:
            return jsonify({'error': f'该分类下还有 {question_count} 道题目，无法删除'}), 400
        
        db.session.delete(category)
        db.session.commit()
        
        return jsonify({'message': '分类删除成功'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'删除分类失败: {str(e)}'}), 500

@category_bp.route('/reorder', methods=['POST'])
@token_required
@admin_required
def reorder_categories(current_user):
    """重新排序分类"""
    try:
        data = request.get_json()
        
        if not data or 'category_orders' not in data:
            return jsonify({'error': '请提供分类排序数据'}), 400
        
        category_orders = data['category_orders']
        
        # 验证数据格式
        if not isinstance(category_orders, list):
            return jsonify({'error': '分类排序数据格式错误'}), 400
        
        # 批量更新排序
        for item in category_orders:
            if not isinstance(item, dict) or 'id' not in item or 'sort_order' not in item:
                return jsonify({'error': '分类排序数据格式错误'}), 400
            
            category = Category.query.get(item['id'])
            if category:
                category.sort_order = item['sort_order']
                category.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({'message': '分类排序更新成功'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'更新分类排序失败: {str(e)}'}), 500