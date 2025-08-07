import requests
from typing import Optional, Dict, Any
import json

class APIClient:
    """API client for backend communication"""
    
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.session = requests.Session()
        self.token = None
    
    def set_token(self, token: str):
        """Set authentication token"""
        self.token = token
        self.session.headers.update({'Authorization': f'Bearer {token}'})
    
    def login(self, username: str, password: str) -> Dict[str, Any]:
        """Login to get access token"""
        response = self.session.post(
            f"{self.base_url}/auth/login",
            data={
                'username': username,
                'password': password,
                'grant_type': 'password'
            }
        )
        if response.status_code == 200:
            data = response.json()
            self.set_token(data['access_token'])
            return data
        else:
            raise Exception(f"Login failed: {response.text}")
    
    def get_current_user(self) -> Dict[str, Any]:
        """Get current user info"""
        response = self.session.get(f"{self.base_url}/auth/me")
        response.raise_for_status()
        return response.json()
    
    # User Management
    def get_users(self, skip: int = 0, limit: int = 100, role: Optional[str] = None) -> list:
        """Get list of users"""
        params = {'skip': skip, 'limit': limit}
        if role:
            params['role'] = role
        response = self.session.get(f"{self.base_url}/users", params=params)
        response.raise_for_status()
        return response.json()
    
    def get_user(self, user_id: int) -> Dict[str, Any]:
        """Get user by ID"""
        response = self.session.get(f"{self.base_url}/users/{user_id}")
        response.raise_for_status()
        return response.json()
    
    def update_user(self, user_id: int, data: Dict[str, Any]) -> Dict[str, Any]:
        """Update user"""
        response = self.session.put(
            f"{self.base_url}/users/{user_id}",
            json=data
        )
        response.raise_for_status()
        return response.json()
    
    def delete_user(self, user_id: int) -> Dict[str, Any]:
        """Delete user"""
        response = self.session.delete(f"{self.base_url}/users/{user_id}")
        response.raise_for_status()
        return response.json()
    
    # Permission Management
    def get_user_permissions(self, user_id: int) -> list:
        """Get user permissions"""
        response = self.session.get(f"{self.base_url}/users/{user_id}/permissions")
        response.raise_for_status()
        return response.json()
    
    def grant_permission(self, user_id: int, bank_id: str, permission: str) -> Dict[str, Any]:
        """Grant permission to user"""
        response = self.session.post(
            f"{self.base_url}/users/{user_id}/permissions",
            params={'bank_id': bank_id, 'permission': permission}
        )
        response.raise_for_status()
        return response.json()
    
    def revoke_permission(self, user_id: int, bank_id: str) -> Dict[str, Any]:
        """Revoke permission from user"""
        response = self.session.delete(
            f"{self.base_url}/users/{user_id}/permissions/{bank_id}"
        )
        response.raise_for_status()
        return response.json()
    
    # Question Bank Management
    def get_question_banks(self, skip: int = 0, limit: int = 100) -> list:
        """Get list of question banks"""
        response = self.session.get(
            f"{self.base_url}/qbank/banks",
            params={'skip': skip, 'limit': limit}
        )
        response.raise_for_status()
        return response.json()
    
    def get_question_bank(self, bank_id: str) -> Dict[str, Any]:
        """Get question bank by ID"""
        response = self.session.get(f"{self.base_url}/qbank/banks/{bank_id}")
        response.raise_for_status()
        return response.json()
    
    def create_question_bank(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create new question bank"""
        response = self.session.post(
            f"{self.base_url}/qbank/banks",
            json=data
        )
        response.raise_for_status()
        return response.json()
    
    def update_question_bank(self, bank_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Update question bank"""
        response = self.session.put(
            f"{self.base_url}/qbank/banks/{bank_id}",
            json=data
        )
        response.raise_for_status()
        return response.json()
    
    def delete_question_bank(self, bank_id: str) -> Dict[str, Any]:
        """Delete question bank"""
        response = self.session.delete(f"{self.base_url}/qbank/banks/{bank_id}")
        response.raise_for_status()
        return response.json()
    
    # Question Management
    def get_questions(self, bank_id: Optional[str] = None, skip: int = 0, limit: int = 100) -> list:
        """Get list of questions"""
        params = {'skip': skip, 'limit': limit}
        if bank_id:
            params['bank_id'] = bank_id
        response = self.session.get(
            f"{self.base_url}/qbank/questions",
            params=params
        )
        response.raise_for_status()
        return response.json()
    
    def get_question(self, question_id: str) -> Dict[str, Any]:
        """Get question by ID"""
        response = self.session.get(f"{self.base_url}/qbank/questions/{question_id}")
        response.raise_for_status()
        return response.json()
    
    def create_question(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create new question"""
        response = self.session.post(
            f"{self.base_url}/qbank/questions",
            json=data
        )
        response.raise_for_status()
        return response.json()
    
    def update_question(self, question_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Update question"""
        response = self.session.put(
            f"{self.base_url}/qbank/questions/{question_id}",
            json=data
        )
        response.raise_for_status()
        return response.json()
    
    def delete_question(self, question_id: str) -> Dict[str, Any]:
        """Delete question"""
        response = self.session.delete(f"{self.base_url}/qbank/questions/{question_id}")
        response.raise_for_status()
        return response.json()
    
    # Import/Export
    def import_csv(self, file, bank_id: str, merge_duplicates: bool = True) -> Dict[str, Any]:
        """Import questions from CSV file"""
        files = {'file': file}
        data = {
            'bank_id': bank_id,
            'merge_duplicates': merge_duplicates
        }
        response = self.session.post(
            f"{self.base_url}/qbank/import/csv",
            files=files,
            data=data
        )
        response.raise_for_status()
        return response.json()
    
    def export_bank(self, bank_id: str, format: str = 'csv'):
        """Export question bank"""
        response = self.session.get(
            f"{self.base_url}/qbank/export/{bank_id}",
            params={'format': format},
            stream=True
        )
        response.raise_for_status()
        return response