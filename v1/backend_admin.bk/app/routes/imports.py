from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app, session, send_file
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
import os
import io

bp = Blueprint('imports', __name__, url_prefix='/imports')

ALLOWED_EXTENSIONS = {'csv', 'json', 'xlsx', 'xls'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@bp.route('/')
@login_required
def index():
    """Import/Export page"""
    try:
        api_client = current_app.api_client
        api_client.set_token(session.get('access_token'))
        
        # Get banks for dropdown
        banks = api_client.get_question_banks(limit=100)
        
        return render_template('imports/index.html', banks=banks)
    except Exception as e:
        flash(f'获取题库列表失败: {str(e)}', 'error')
        return render_template('imports/index.html', banks=[])

@bp.route('/upload', methods=['POST'])
@login_required
def upload():
    """Upload and import file"""
    try:
        api_client = current_app.api_client
        api_client.set_token(session.get('access_token'))
        
        # Check if file is present
        if 'file' not in request.files:
            flash('请选择文件', 'error')
            return redirect(url_for('imports.index'))
        
        file = request.files['file']
        
        if file.filename == '':
            flash('请选择文件', 'error')
            return redirect(url_for('imports.index'))
        
        if not allowed_file(file.filename):
            flash('不支持的文件格式', 'error')
            return redirect(url_for('imports.index'))
        
        # Get form data
        bank_id = request.form.get('bank_id')
        merge_duplicates = request.form.get('merge_duplicates') == 'on'
        
        if not bank_id:
            flash('请选择题库', 'error')
            return redirect(url_for('imports.index'))
        
        # Determine file type and call appropriate API
        filename = secure_filename(file.filename)
        file_ext = filename.rsplit('.', 1)[1].lower()
        
        if file_ext == 'csv':
            result = api_client.import_csv(file, bank_id, merge_duplicates)
        elif file_ext == 'json':
            # TODO: Implement JSON import
            flash('JSON导入功能开发中', 'info')
            return redirect(url_for('imports.index'))
        else:
            flash('不支持的文件格式', 'error')
            return redirect(url_for('imports.index'))
        
        # Show results
        if result.get('success'):
            flash(f"导入成功: {result.get('imported_count', 0)} 题", 'success')
            if result.get('failed_count', 0) > 0:
                flash(f"失败: {result.get('failed_count')} 题", 'warning')
        else:
            flash('导入失败', 'error')
        
        return redirect(url_for('imports.index'))
        
    except Exception as e:
        flash(f'导入失败: {str(e)}', 'error')
        return redirect(url_for('imports.index'))

@bp.route('/export/<bank_id>')
@login_required
def export(bank_id):
    """Export question bank"""
    try:
        api_client = current_app.api_client
        api_client.set_token(session.get('access_token'))
        
        # Get export format
        format = request.args.get('format', 'csv')
        
        # Get bank data
        response = api_client.export_bank(bank_id, format)
        
        # Create file-like object
        file_data = io.BytesIO()
        for chunk in response.iter_content(chunk_size=8192):
            file_data.write(chunk)
        file_data.seek(0)
        
        # Determine filename and mimetype
        if format == 'csv':
            filename = f'export_{bank_id}.csv'
            mimetype = 'text/csv'
        else:
            filename = f'export_{bank_id}.json'
            mimetype = 'application/json'
        
        return send_file(
            file_data,
            mimetype=mimetype,
            as_attachment=True,
            download_name=filename
        )
        
    except Exception as e:
        flash(f'导出失败: {str(e)}', 'error')
        return redirect(url_for('imports.index'))

@bp.route('/template')
@login_required
def download_template():
    """Download import template"""
    # Create CSV template
    csv_content = "题号,题干,A,B,C,D,E,答案,难度,题型\n"
    csv_content += "1,以下哪个是Python的关键字？,if,hello,123,world,,A,easy,单选\n"
    csv_content += "2,以下哪些是编程语言？,Python,Word,Java,Excel,C++,ACE,medium,多选\n"
    
    # Create file-like object
    file_data = io.BytesIO(csv_content.encode('utf-8-sig'))
    file_data.seek(0)
    
    return send_file(
        file_data,
        mimetype='text/csv',
        as_attachment=True,
        download_name='import_template.csv'
    )