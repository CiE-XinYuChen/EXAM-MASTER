from flask_login import UserMixin
from typing import Dict, Any

class User(UserMixin):
    """User class for Flask-Login"""
    
    def __init__(self, user_data: Dict[str, Any]):
        self.id = user_data.get('id')
        self.username = user_data.get('username')
        self.email = user_data.get('email')
        self.role = user_data.get('role')
        self.is_active = user_data.get('is_active', True)
        self._authenticated = True
    
    def get_id(self):
        return str(self.id)
    
    @property
    def is_authenticated(self):
        return self._authenticated
    
    @property
    def is_admin(self):
        return self.role == 'admin'
    
    @property
    def is_teacher(self):
        return self.role in ['admin', 'teacher']
    
    def can_manage_users(self):
        return self.is_admin
    
    def can_manage_banks(self):
        return self.is_teacher