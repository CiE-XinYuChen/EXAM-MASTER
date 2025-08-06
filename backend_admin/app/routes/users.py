from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app, session, jsonify
from flask_login import login_required, current_user
from functools import wraps

bp = Blueprint('users', __name__, url_prefix='/users')

def admin_required(f):
    """Decorator to require admin role"""
    @wraps(f)
    @login_required
    def decorated_function(*args, **kwargs):
        if not current_user.is_admin:
            flash('您没有权限访问此页面', 'error')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

@bp.route('/')
@admin_required
def list():
    """List all users"""
    try:
        api_client = current_app.api_client
        api_client.set_token(session.get('access_token'))
        
        # Get pagination parameters
        page = request.args.get('page', 1, type=int)
        per_page = 20
        skip = (page - 1) * per_page
        
        # Get filter parameters
        role = request.args.get('role')
        
        # Fetch users from API
        users = api_client.get_users(skip=skip, limit=per_page, role=role)
        
        return render_template('users/list.html', users=users, page=page)
    except Exception as e:
        flash(f'获取用户列表失败: {str(e)}', 'error')
        return render_template('users/list.html', users=[], page=1)

@bp.route('/create', methods=['GET', 'POST'])
@admin_required
def create():
    """Create new user"""
    if request.method == 'POST':
        try:
            api_client = current_app.api_client
            api_client.set_token(session.get('access_token'))
            
            # Get form data
            data = {
                'username': request.form.get('username'),
                'email': request.form.get('email'),
                'password': request.form.get('password'),
                'role': request.form.get('role', 'student'),
                'is_active': request.form.get('is_active') == 'on'
            }
            
            # TODO: Call API to create user (requires register endpoint for admin)
            flash('用户创建功能需要后端API支持', 'info')
            return redirect(url_for('users.list'))
            
        except Exception as e:
            flash(f'创建用户失败: {str(e)}', 'error')
    
    return render_template('users/form.html', user=None)

@bp.route('/<int:user_id>/edit', methods=['GET', 'POST'])
@admin_required
def edit(user_id):
    """Edit user"""
    api_client = current_app.api_client
    api_client.set_token(session.get('access_token'))
    
    if request.method == 'POST':
        try:
            # Get form data
            data = {
                'email': request.form.get('email'),
                'role': request.form.get('role'),
                'is_active': request.form.get('is_active') == 'on'
            }
            
            # Update user
            api_client.update_user(user_id, data)
            flash('用户更新成功', 'success')
            return redirect(url_for('users.list'))
            
        except Exception as e:
            flash(f'更新用户失败: {str(e)}', 'error')
    
    try:
        # Get user data
        user = api_client.get_user(user_id)
        return render_template('users/form.html', user=user)
    except Exception as e:
        flash(f'获取用户信息失败: {str(e)}', 'error')
        return redirect(url_for('users.list'))

@bp.route('/<int:user_id>/delete', methods=['POST'])
@admin_required
def delete(user_id):
    """Delete user"""
    try:
        api_client = current_app.api_client
        api_client.set_token(session.get('access_token'))
        
        api_client.delete_user(user_id)
        flash('用户删除成功', 'success')
    except Exception as e:
        flash(f'删除用户失败: {str(e)}', 'error')
    
    return redirect(url_for('users.list'))

@bp.route('/permissions')
@admin_required
def permissions():
    """Manage user permissions"""
    try:
        api_client = current_app.api_client
        api_client.set_token(session.get('access_token'))
        
        # Get all users
        users = api_client.get_users(limit=1000)
        
        # Get all question banks
        banks = api_client.get_question_banks(limit=1000)
        
        return render_template('users/permissions.html', users=users, banks=banks)
    except Exception as e:
        flash(f'获取权限信息失败: {str(e)}', 'error')
        return render_template('users/permissions.html', users=[], banks=[])

@bp.route('/<int:user_id>/permissions', methods=['GET'])
@admin_required
def get_permissions(user_id):
    """Get user permissions (API endpoint)"""
    try:
        api_client = current_app.api_client
        api_client.set_token(session.get('access_token'))
        
        permissions = api_client.get_user_permissions(user_id)
        return jsonify(permissions)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/<int:user_id>/permissions', methods=['POST'])
@admin_required
def grant_permission(user_id):
    """Grant permission to user"""
    try:
        api_client = current_app.api_client
        api_client.set_token(session.get('access_token'))
        
        bank_id = request.json.get('bank_id')
        permission = request.json.get('permission')
        
        result = api_client.grant_permission(user_id, bank_id, permission)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/<int:user_id>/permissions/<bank_id>', methods=['DELETE'])
@admin_required
def revoke_permission(user_id, bank_id):
    """Revoke permission from user"""
    try:
        api_client = current_app.api_client
        api_client.set_token(session.get('access_token'))
        
        result = api_client.revoke_permission(user_id, bank_id)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500