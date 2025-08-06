from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app, session, jsonify
from flask_login import login_required, current_user
from functools import wraps

bp = Blueprint('qbanks', __name__, url_prefix='/qbanks')

def teacher_required(f):
    """Decorator to require teacher or admin role"""
    @wraps(f)
    @login_required
    def decorated_function(*args, **kwargs):
        if not current_user.is_teacher:
            flash('您没有权限访问此页面', 'error')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

@bp.route('/')
@login_required
def list():
    """List question banks"""
    try:
        api_client = current_app.api_client
        api_client.set_token(session.get('access_token'))
        
        # Get pagination parameters
        page = request.args.get('page', 1, type=int)
        per_page = 20
        skip = (page - 1) * per_page
        
        # Fetch banks from API
        banks = api_client.get_question_banks(skip=skip, limit=per_page)
        
        return render_template('qbanks/list.html', banks=banks, page=page)
    except Exception as e:
        flash(f'获取题库列表失败: {str(e)}', 'error')
        return render_template('qbanks/list.html', banks=[], page=1)

@bp.route('/create', methods=['GET', 'POST'])
@teacher_required
def create():
    """Create new question bank"""
    if request.method == 'POST':
        try:
            api_client = current_app.api_client
            api_client.set_token(session.get('access_token'))
            
            # Get form data
            data = {
                'name': request.form.get('name'),
                'description': request.form.get('description'),
                'category': request.form.get('category'),
                'is_public': request.form.get('is_public') == 'on'
            }
            
            # Create bank
            bank = api_client.create_question_bank(data)
            flash('题库创建成功', 'success')
            return redirect(url_for('qbanks.view', bank_id=bank['id']))
            
        except Exception as e:
            flash(f'创建题库失败: {str(e)}', 'error')
    
    return render_template('qbanks/form.html', bank=None)

@bp.route('/<bank_id>')
@login_required
def view(bank_id):
    """View question bank details"""
    try:
        api_client = current_app.api_client
        api_client.set_token(session.get('access_token'))
        
        # Get bank details
        bank = api_client.get_question_bank(bank_id)
        
        # Get questions in this bank
        questions = api_client.get_questions(bank_id=bank_id)
        
        return render_template('qbanks/view.html', bank=bank, questions=questions)
    except Exception as e:
        flash(f'获取题库详情失败: {str(e)}', 'error')
        return redirect(url_for('qbanks.list'))

@bp.route('/<bank_id>/edit', methods=['GET', 'POST'])
@teacher_required
def edit(bank_id):
    """Edit question bank"""
    api_client = current_app.api_client
    api_client.set_token(session.get('access_token'))
    
    if request.method == 'POST':
        try:
            # Get form data
            data = {
                'name': request.form.get('name'),
                'description': request.form.get('description'),
                'category': request.form.get('category'),
                'is_public': request.form.get('is_public') == 'on'
            }
            
            # Update bank
            api_client.update_question_bank(bank_id, data)
            flash('题库更新成功', 'success')
            return redirect(url_for('qbanks.view', bank_id=bank_id))
            
        except Exception as e:
            flash(f'更新题库失败: {str(e)}', 'error')
    
    try:
        # Get bank data
        bank = api_client.get_question_bank(bank_id)
        return render_template('qbanks/form.html', bank=bank)
    except Exception as e:
        flash(f'获取题库信息失败: {str(e)}', 'error')
        return redirect(url_for('qbanks.list'))

@bp.route('/<bank_id>/delete', methods=['POST'])
@teacher_required
def delete(bank_id):
    """Delete question bank"""
    try:
        api_client = current_app.api_client
        api_client.set_token(session.get('access_token'))
        
        api_client.delete_question_bank(bank_id)
        flash('题库删除成功', 'success')
    except Exception as e:
        flash(f'删除题库失败: {str(e)}', 'error')
    
    return redirect(url_for('qbanks.list'))

@bp.route('/<bank_id>/clone', methods=['POST'])
@teacher_required
def clone(bank_id):
    """Clone question bank"""
    try:
        api_client = current_app.api_client
        api_client.set_token(session.get('access_token'))
        
        new_name = request.form.get('new_name', 'Clone')
        
        # TODO: Call clone API endpoint
        flash('克隆功能需要后端API支持', 'info')
        
    except Exception as e:
        flash(f'克隆题库失败: {str(e)}', 'error')
    
    return redirect(url_for('qbanks.list'))