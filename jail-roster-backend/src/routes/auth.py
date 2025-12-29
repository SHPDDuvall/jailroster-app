from flask import Blueprint, request, jsonify, session
import hashlib
import secrets
from datetime import datetime, timedelta

auth_bp = Blueprint('auth', __name__)

# In-memory user storage for demo purposes
# In production, this should be stored in a secure database with proper password hashing
users = {
    'admin': {
        'password_hash': hashlib.sha256('admin123'.encode()).hexdigest(),
        'role': 'administrator',
        'name': 'System Administrator'
    },
    'officer': {
        'password_hash': hashlib.sha256('officer123'.encode()).hexdigest(),
        'role': 'officer',
        'name': 'Corrections Officer'
    },
    'supervisor': {
        'password_hash': hashlib.sha256('supervisor123'.encode()).hexdigest(),
        'role': 'supervisor',
        'name': 'Jail Supervisor'
    }
}

def hash_password(password):
    """Hash a password for storing."""
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(stored_password_hash, provided_password):
    """Verify a stored password against provided password."""
    return stored_password_hash == hashlib.sha256(provided_password.encode()).hexdigest()

@auth_bp.route('/login', methods=['POST'])
def login():
    """Authenticate user and create session"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        username = data.get('username', '').strip().lower()
        password = data.get('password', '')
        
        if not username or not password:
            return jsonify({'error': 'Username and password are required'}), 400
        
        # Check if user exists and password is correct
        user = users.get(username)
        if not user or not verify_password(user['password_hash'], password):
            return jsonify({'error': 'Invalid username or password'}), 401
        
        # Create session
        session['user_id'] = username
        session['user_role'] = user['role']
        session['user_name'] = user['name']
        session['login_time'] = datetime.now().isoformat()
        session.permanent = True
        
        return jsonify({
            'message': 'Login successful',
            'user': {
                'username': username,
                'name': user['name'],
                'role': user['role']
            }
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/logout', methods=['POST'])
def logout():
    """Logout user and clear session"""
    try:
        session.clear()
        return jsonify({'message': 'Logout successful'}), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/me', methods=['GET'])
def get_current_user():
    """Get current user information"""
    try:
        if 'user_id' not in session:
            return jsonify({'error': 'Not authenticated'}), 401
        
        username = session['user_id']
        user = users.get(username)
        
        if not user:
            session.clear()
            return jsonify({'error': 'User not found'}), 401
        
        return jsonify({
            'user': {
                'username': username,
                'name': session.get('user_name'),
                'role': session.get('user_role'),
                'login_time': session.get('login_time')
            }
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/change-password', methods=['POST'])
def change_password():
    """Change user password"""
    try:
        if 'user_id' not in session:
            return jsonify({'error': 'Not authenticated'}), 401
        
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        current_password = data.get('current_password', '')
        new_password = data.get('new_password', '')
        
        if not current_password or not new_password:
            return jsonify({'error': 'Current password and new password are required'}), 400
        
        if len(new_password) < 6:
            return jsonify({'error': 'New password must be at least 6 characters long'}), 400
        
        username = session['user_id']
        user = users.get(username)
        
        if not user or not verify_password(user['password_hash'], current_password):
            return jsonify({'error': 'Current password is incorrect'}), 401
        
        # Update password
        users[username]['password_hash'] = hash_password(new_password)
        
        return jsonify({'message': 'Password changed successfully'}), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def require_auth(f):
    """Decorator to require authentication for routes"""
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'error': 'Authentication required'}), 401
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

def require_role(required_role):
    """Decorator to require specific role for routes"""
    def decorator(f):
        def decorated_function(*args, **kwargs):
            if 'user_id' not in session:
                return jsonify({'error': 'Authentication required'}), 401
            
            user_role = session.get('user_role')
            if user_role != required_role and user_role != 'administrator':
                return jsonify({'error': 'Insufficient permissions'}), 403
            
            return f(*args, **kwargs)
        decorated_function.__name__ = f.__name__
        return decorated_function
    return decorator
