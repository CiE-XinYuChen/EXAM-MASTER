from flask import Blueprint, render_template, redirect, url_for, flash, request, session, current_app
from flask_login import login_user, logout_user, login_required
from app.utils.auth import User

bp = Blueprint('auth', __name__, url_prefix='/auth')

@bp.route('/login', methods=['GET', 'POST'])
def login():
    """Login page and handler"""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if not username or not password:
            flash('请输入用户名和密码', 'error')
            return render_template('auth/login.html')
        
        try:
            # Call API to login
            api_client = current_app.api_client
            login_data = api_client.login(username, password)
            
            # Get user info
            user_data = api_client.get_current_user()
            
            # Store user data in session
            session['user_data'] = user_data
            session['access_token'] = login_data['access_token']
            
            # Create user object and login
            user = User(user_data)
            login_user(user, remember=True)
            
            # Redirect to next page or dashboard
            next_page = request.args.get('next')
            if next_page:
                return redirect(next_page)
            return redirect(url_for('index'))
            
        except Exception as e:
            flash(f'登录失败: {str(e)}', 'error')
            return render_template('auth/login.html')
    
    return render_template('auth/login.html')

@bp.route('/logout')
@login_required
def logout():
    """Logout handler"""
    logout_user()
    session.clear()
    flash('您已成功退出登录', 'success')
    return redirect(url_for('auth.login'))