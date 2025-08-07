from flask import Flask, render_template, redirect, url_for, flash, request, session
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_session import Session
import os
from dotenv import load_dotenv
from app.routes import auth, users, qbanks, questions, imports
from app.services.api_client import APIClient
from app.utils.auth import User

# Load environment variables
load_dotenv()

# Create Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key')
app.config['SESSION_TYPE'] = 'filesystem'
app.config['API_BASE_URL'] = os.getenv('API_BASE_URL', 'http://localhost:8000/api/v1')

# Initialize Flask-Session
Session(app)

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth.login'
login_manager.login_message = '请先登录'

# Initialize API client
api_client = APIClient(app.config['API_BASE_URL'])
app.api_client = api_client

@login_manager.user_loader
def load_user(user_id):
    """Load user from session"""
    if 'user_data' in session:
        user_data = session['user_data']
        if str(user_data.get('id')) == str(user_id):
            return User(user_data)
    return None

# Register blueprints
app.register_blueprint(auth.bp)
app.register_blueprint(users.bp)
app.register_blueprint(qbanks.bp)
app.register_blueprint(questions.bp)
app.register_blueprint(imports.bp)

@app.route('/')
@login_required
def index():
    """Dashboard page"""
    return render_template('dashboard.html')

@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    return render_template('500.html'), 500

@app.context_processor
def inject_user():
    """Inject current user into all templates"""
    return dict(current_user=current_user)

if __name__ == '__main__':
    app.run(debug=True, port=5000)