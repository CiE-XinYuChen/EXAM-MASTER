from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app, session, jsonify
from flask_login import login_required, current_user

bp = Blueprint('questions', __name__, url_prefix='/questions')

@bp.route('/')
@login_required
def list():
    """List questions"""
    try:
        api_client = current_app.api_client
        api_client.set_token(session.get('access_token'))
        
        # Get filter parameters
        bank_id = request.args.get('bank_id')
        q_type = request.args.get('type')
        difficulty = request.args.get('difficulty')
        search = request.args.get('search')
        
        # Get pagination
        page = request.args.get('page', 1, type=int)
        per_page = 20
        skip = (page - 1) * per_page
        
        # Fetch questions
        questions = api_client.get_questions(
            bank_id=bank_id,
            skip=skip,
            limit=per_page
        )
        
        # Get banks for filter dropdown
        banks = api_client.get_question_banks(limit=100)
        
        return render_template('questions/list.html', 
                             questions=questions, 
                             banks=banks,
                             page=page,
                             filters={
                                 'bank_id': bank_id,
                                 'type': q_type,
                                 'difficulty': difficulty,
                                 'search': search
                             })
    except Exception as e:
        flash(f'获取题目列表失败: {str(e)}', 'error')
        return render_template('questions/list.html', questions=[], banks=[], page=1, filters={})

@bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    """Create new question"""
    api_client = current_app.api_client
    api_client.set_token(session.get('access_token'))
    
    if request.method == 'POST':
        try:
            # Get form data
            data = {
                'bank_id': request.form.get('bank_id'),
                'question_number': int(request.form.get('question_number', 0)),
                'stem': request.form.get('stem'),
                'type': request.form.get('type'),
                'difficulty': request.form.get('difficulty'),
                'category': request.form.get('category'),
                'explanation': request.form.get('explanation'),
                'options': []
            }
            
            # Get options
            option_labels = request.form.getlist('option_label[]')
            option_contents = request.form.getlist('option_content[]')
            option_corrects = request.form.getlist('option_correct[]')
            
            for i, label in enumerate(option_labels):
                if i < len(option_contents):
                    data['options'].append({
                        'label': label,
                        'content': option_contents[i],
                        'is_correct': str(i) in option_corrects
                    })
            
            # Create question
            question = api_client.create_question(data)
            flash('题目创建成功', 'success')
            return redirect(url_for('questions.view', question_id=question['id']))
            
        except Exception as e:
            flash(f'创建题目失败: {str(e)}', 'error')
    
    # Get banks for dropdown
    try:
        banks = api_client.get_question_banks(limit=100)
    except:
        banks = []
    
    return render_template('questions/form.html', question=None, banks=banks)

@bp.route('/<question_id>')
@login_required
def view(question_id):
    """View question details"""
    try:
        api_client = current_app.api_client
        api_client.set_token(session.get('access_token'))
        
        question = api_client.get_question(question_id)
        return render_template('questions/view.html', question=question)
    except Exception as e:
        flash(f'获取题目详情失败: {str(e)}', 'error')
        return redirect(url_for('questions.list'))

@bp.route('/<question_id>/edit', methods=['GET', 'POST'])
@login_required
def edit(question_id):
    """Edit question"""
    api_client = current_app.api_client
    api_client.set_token(session.get('access_token'))
    
    if request.method == 'POST':
        try:
            # Get form data
            data = {
                'stem': request.form.get('stem'),
                'type': request.form.get('type'),
                'difficulty': request.form.get('difficulty'),
                'category': request.form.get('category'),
                'explanation': request.form.get('explanation')
            }
            
            # Update question
            api_client.update_question(question_id, data)
            flash('题目更新成功', 'success')
            return redirect(url_for('questions.view', question_id=question_id))
            
        except Exception as e:
            flash(f'更新题目失败: {str(e)}', 'error')
    
    try:
        question = api_client.get_question(question_id)
        banks = api_client.get_question_banks(limit=100)
        return render_template('questions/form.html', question=question, banks=banks)
    except Exception as e:
        flash(f'获取题目信息失败: {str(e)}', 'error')
        return redirect(url_for('questions.list'))

@bp.route('/<question_id>/delete', methods=['POST'])
@login_required
def delete(question_id):
    """Delete question"""
    try:
        api_client = current_app.api_client
        api_client.set_token(session.get('access_token'))
        
        api_client.delete_question(question_id)
        flash('题目删除成功', 'success')
    except Exception as e:
        flash(f'删除题目失败: {str(e)}', 'error')
    
    return redirect(url_for('questions.list'))