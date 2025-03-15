from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity, verify_jwt_in_request
from models import User, Role
from extensions import db
from email_validator import validate_email, EmailNotValidError
import re
from functools import wraps

auth_bp = Blueprint('auth', __name__)

# Custom JWT required decorator with better error handling
def jwt_required_custom(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        try:
            verify_jwt_in_request()
            return fn(*args, **kwargs)
        except Exception as e:
            return jsonify({'error': str(e)}), 401
    
    return wrapper

# Custom JWT required decorator for refresh token
def jwt_refresh_required_custom(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        try:
            verify_jwt_in_request(refresh=True)
            return fn(*args, **kwargs)
        except Exception as e:
            return jsonify({'error': str(e)}), 401
    
    return wrapper

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    
    # Validate required fields
    required_fields = ['email', 'password', 'first_name', 'last_name', 'student_id']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'Missing required field: {field}'}), 400
    
    # Validate email format
    try:
        valid = validate_email(data['email'])
        email = valid.email
    except EmailNotValidError as e:
        return jsonify({'error': str(e)}), 400
    
    # Check if email already exists
    if User.query.filter_by(email=email).first():
        return jsonify({'error': 'Email already registered'}), 400
    
    # Check if student ID already exists
    if User.query.filter_by(student_id=data['student_id']).first():
        return jsonify({'error': 'Student ID already registered'}), 400
    
    # Validate password strength
    if len(data['password']) < 8:
        return jsonify({'error': 'Password must be at least 8 characters long'}), 400
    
    # Create new user
    new_user = User(
        email=email,
        student_id=data['student_id'],
        first_name=data['first_name'],
        last_name=data['last_name']
    )
    new_user.password = data['password']  # This will hash the password
    
    # Assign default role (Student)
    student_role = Role.query.filter_by(name='Student').first()
    if not student_role:
        student_role = Role(name='Student', description='Regular student user')
        db.session.add(student_role)
    
    new_user.roles.append(student_role)
    
    # Save to database
    db.session.add(new_user)
    db.session.commit()
    
    # Generate tokens
    access_token = create_access_token(identity=new_user.id)
    refresh_token = create_refresh_token(identity=new_user.id)
    
    return jsonify({
        'message': 'User registered successfully',
        'user': new_user.to_dict(),
        'access_token': access_token,
        'refresh_token': refresh_token
    }), 201

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    
    # Check if required fields are present
    if not data or not data.get('id_or_email') or not data.get('password'):
        return jsonify({'error': 'Missing login credentials'}), 400
    
    id_or_email = data.get('id_or_email')
    password = data.get('password')
    
    # Check if input is email or student ID
    is_email = '@' in id_or_email
    
    # Find user by email or student ID
    if is_email:
        user = User.query.filter_by(email=id_or_email).first()
    else:
        user = User.query.filter_by(student_id=id_or_email).first()
    
    # Check if user exists and password is correct
    if not user or not user.verify_password(password):
        return jsonify({'error': 'Invalid credentials'}), 401
    
    # Check if user is active
    if not user.is_active:
        return jsonify({'error': 'Account is deactivated. Please contact administrator.'}), 403
    
    # Generate tokens
    access_token = create_access_token(identity=user.id)
    refresh_token = create_refresh_token(identity=user.id)
    
    return jsonify({
        'message': 'Login successful',
        'user': user.to_dict(),
        'access_token': access_token,
        'refresh_token': refresh_token
    }), 200

@auth_bp.route('/refresh', methods=['POST'])
@jwt_refresh_required_custom
def refresh():
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    if not user.is_active:
        return jsonify({'error': 'Account is deactivated'}), 403
    
    access_token = create_access_token(identity=current_user_id)
    
    return jsonify({
        'access_token': access_token,
        'user': user.to_dict()
    }), 200

@auth_bp.route('/me', methods=['GET'])
@jwt_required_custom
def get_current_user():
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    return jsonify(user.to_dict()), 200

@auth_bp.route('/forgot-password', methods=['POST'])
def forgot_password():
    data = request.get_json()
    
    if not data or not data.get('email'):
        return jsonify({'error': 'Email is required'}), 400
    
    email = data.get('email')
    user = User.query.filter_by(email=email).first()
    
    if not user:
        # For security reasons, don't reveal that the user doesn't exist
        return jsonify({'message': 'If your email is registered, you will receive a password reset link'}), 200
    
    # In a real application, you would generate a token and send an email
    # For this example, we'll just return a success message
    
    return jsonify({'message': 'If your email is registered, you will receive a password reset link'}), 200

@auth_bp.route('/reset-password', methods=['POST'])
def reset_password():
    data = request.get_json()
    
    if not data or not data.get('token') or not data.get('password'):
        return jsonify({'error': 'Token and new password are required'}), 400
    
    # In a real application, you would validate the token and update the password
    # For this example, we'll just return a success message
    
    return jsonify({'message': 'Password has been reset successfully'}), 200 