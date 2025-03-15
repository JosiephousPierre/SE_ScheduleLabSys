from flask import Blueprint, request, jsonify, send_file
from flask_jwt_extended import jwt_required, get_jwt_identity, verify_jwt_in_request
from models import User, Role, Permission, ProfilePic
from extensions import db
from functools import wraps
import base64
import io
from PIL import Image

user_bp = Blueprint('users', __name__)

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

# Custom decorator to check if user has admin role
def admin_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        try:
            verify_jwt_in_request()
            current_user_id = get_jwt_identity()
            user = User.query.get(current_user_id)
            
            if not user or not user.has_role('System Administrator'):
                return jsonify({'error': 'Admin privileges required'}), 403
            
            return fn(*args, **kwargs)
        except Exception as e:
            return jsonify({'error': str(e)}), 401
    
    return wrapper

@user_bp.route('/', methods=['GET'])
@jwt_required_custom
def get_all_users():
    # Check if role parameter is provided
    role = request.args.get('role')
    first_name = request.args.get('first_name')
    last_name = request.args.get('last_name')
    
    # Start with base query
    query = User.query
    
    # Apply filters if provided
    if role:
        # Join with roles to filter by role name
        query = query.join(User.roles).filter(Role.name == role)
    
    if first_name:
        query = query.filter(User.first_name == first_name)
    
    if last_name:
        query = query.filter(User.last_name == last_name)
    
    # Execute query
    users = query.all()
    
    return jsonify([user.to_dict() for user in users]), 200

@user_bp.route('/<int:user_id>', methods=['GET'])
@jwt_required_custom
def get_user(user_id):
    current_user_id = get_jwt_identity()
    current_user = User.query.get(current_user_id)
    
    # Only allow admins to view other users' details
    if current_user_id != user_id and not current_user.has_role('System Administrator'):
        return jsonify({'error': 'Unauthorized to view this user'}), 403
    
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    return jsonify(user.to_dict()), 200

@user_bp.route('/', methods=['POST'])
@admin_required
def create_user():
    data = request.get_json()
    
    # Validate required fields
    required_fields = ['email', 'password', 'first_name', 'last_name', 'student_id', 'roles']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'Missing required field: {field}'}), 400
    
    # Check if email already exists
    if User.query.filter_by(email=data['email']).first():
        return jsonify({'error': 'Email already registered'}), 400
    
    # Check if student ID already exists
    if User.query.filter_by(student_id=data['student_id']).first():
        return jsonify({'error': 'Student ID already registered'}), 400
    
    # Create new user
    new_user = User(
        email=data['email'],
        student_id=data['student_id'],
        first_name=data['first_name'],
        last_name=data['last_name']
    )
    new_user.password = data['password']  # This will hash the password
    
    # Assign roles
    for role_name in data['roles']:
        role = Role.query.filter_by(name=role_name).first()
        if role:
            new_user.roles.append(role)
    
    # Save to database
    db.session.add(new_user)
    db.session.commit()
    
    return jsonify({
        'message': 'User created successfully',
        'user': new_user.to_dict()
    }), 201

@user_bp.route('/<int:user_id>', methods=['PUT'])
@jwt_required_custom
def update_user(user_id):
    current_user_id = get_jwt_identity()
    current_user = User.query.get(current_user_id)
    
    # Only allow users to update their own profile or admins to update any profile
    if current_user_id != user_id and not current_user.has_role('System Administrator'):
        return jsonify({'error': 'Unauthorized to update this user'}), 403
    
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    data = request.get_json()
    
    # Update basic info
    if 'first_name' in data:
        user.first_name = data['first_name']
    
    if 'last_name' in data:
        user.last_name = data['last_name']
    
    # Only admins can update roles and permissions
    if current_user.has_role('System Administrator'):
        if 'roles' in data:
            # Clear existing roles
            user.roles = []
            
            # Assign new roles
            for role_name in data['roles']:
                role = Role.query.filter_by(name=role_name).first()
                if role:
                    user.roles.append(role)
        
        if 'is_active' in data:
            user.is_active = data['is_active']
    
    # Update password if provided
    if 'password' in data:
        user.password = data['password']
    
    db.session.commit()
    
    return jsonify({
        'message': 'User updated successfully',
        'user': user.to_dict()
    }), 200

@user_bp.route('/<int:user_id>', methods=['DELETE'])
@admin_required
def delete_user(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    db.session.delete(user)
    db.session.commit()
    
    return jsonify({'message': 'User deleted successfully'}), 200

@user_bp.route('/roles', methods=['GET'])
@jwt_required_custom
def get_all_roles():
    roles = Role.query.all()
    return jsonify([role.to_dict() for role in roles]), 200

@user_bp.route('/roles', methods=['POST'])
@admin_required
def create_role():
    data = request.get_json()
    
    if not data or not data.get('name'):
        return jsonify({'error': 'Role name is required'}), 400
    
    # Check if role already exists
    if Role.query.filter_by(name=data['name']).first():
        return jsonify({'error': 'Role already exists'}), 400
    
    # Create new role
    new_role = Role(
        name=data['name'],
        description=data.get('description', '')
    )
    
    # Assign permissions if provided
    if 'permissions' in data:
        for perm_name in data['permissions']:
            perm = Permission.query.filter_by(name=perm_name).first()
            if perm:
                new_role.permissions.append(perm)
    
    db.session.add(new_role)
    db.session.commit()
    
    return jsonify({
        'message': 'Role created successfully',
        'role': new_role.to_dict()
    }), 201

@user_bp.route('/permissions', methods=['GET'])
@jwt_required_custom
def get_all_permissions():
    permissions = Permission.query.all()
    return jsonify([perm.to_dict() for perm in permissions]), 200

@user_bp.route('/permissions', methods=['POST'])
@admin_required
def create_permission():
    data = request.get_json()
    
    if not data or not data.get('name'):
        return jsonify({'error': 'Permission name is required'}), 400
    
    # Check if permission already exists
    if Permission.query.filter_by(name=data['name']).first():
        return jsonify({'error': 'Permission already exists'}), 400
    
    # Create new permission
    new_permission = Permission(
        name=data['name'],
        description=data.get('description', '')
    )
    
    db.session.add(new_permission)
    db.session.commit()
    
    return jsonify({
        'message': 'Permission created successfully',
        'permission': new_permission.to_dict()
    }), 201

@user_bp.route('/profile-pic/<int:user_id>', methods=['POST'])
def upload_profile_pic(user_id):
    try:
        # Check if user exists
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Debug: Print request information
        print(f"Request method: {request.method}")
        print(f"Request content type: {request.content_type}")
        print(f"Request files: {request.files}")
        print(f"Request form: {request.form}")
        
        if 'image' not in request.files:
            return jsonify({'error': 'No image file provided'}), 400
        
        image_file = request.files['image']
        if image_file.filename == '':
            return jsonify({'error': 'No image file selected'}), 400
        
        try:
            # Resize the image to reduce its size
            # Open the image using PIL
            img = Image.open(image_file)
            
            # Convert RGBA to RGB if the image has an alpha channel
            if img.mode == 'RGBA':
                # Create a white background image
                background = Image.new('RGB', img.size, (255, 255, 255))
                # Paste the image on the background using the alpha channel as mask
                background.paste(img, mask=img.split()[3])  # 3 is the alpha channel
                img = background
            elif img.mode != 'RGB':
                # Convert any other mode to RGB
                img = img.convert('RGB')
            
            # Resize the image to a maximum of 300x300 pixels while preserving aspect ratio
            max_size = (300, 300)
            img.thumbnail(max_size, Image.LANCZOS)
            
            # Convert the image to JPEG format with reduced quality to save space
            output = io.BytesIO()
            img.save(output, format='JPEG', quality=85)
            image_data = output.getvalue()
            
            # Reset the file pointer to the beginning for reading
            image_file.seek(0)
            print(f"Original image size: {len(image_file.read())} bytes")
            print(f"Resized image size: {len(image_data)} bytes")
        except Exception as img_error:
            print(f"Error processing image: {str(img_error)}")
            return jsonify({'error': f'Error processing image: {str(img_error)}'}), 400
        
        # Check if user already has a profile pic
        profile_pic = ProfilePic.query.filter_by(id=user_id).first()
        
        if profile_pic:
            # Update existing profile pic
            profile_pic.image = image_data
        else:
            # Create new profile pic
            new_profile_pic = ProfilePic(id=user_id, image=image_data)
            db.session.add(new_profile_pic)
        
        # Commit the changes
        db.session.commit()
        
        return jsonify({
            'message': 'Profile picture uploaded successfully',
            'user': user.to_dict()
        }), 200
    except Exception as e:
        db.session.rollback()
        import traceback
        error_traceback = traceback.format_exc()
        print(f"Error in upload_profile_pic: {str(e)}")
        print(error_traceback)
        return jsonify({'error': str(e), 'traceback': error_traceback}), 500

@user_bp.route('/profile-pic/<int:user_id>', methods=['GET'])
def get_profile_pic(user_id):
    try:
        profile_pic = ProfilePic.query.filter_by(id=user_id).first()
        
        if not profile_pic or not profile_pic.image:
            return jsonify({'error': 'Profile picture not found', 'has_profile_pic': False}), 404
        
        # Create a BytesIO object from the image data
        image_binary = io.BytesIO(profile_pic.image)
        image_binary.seek(0)
        
        # Try to determine the image format
        try:
            img = Image.open(image_binary)
            mimetype = f'image/{img.format.lower()}' if img.format else 'image/jpeg'
            image_binary.seek(0)  # Reset the file pointer after reading
        except Exception:
            # Default to JPEG if format detection fails
            mimetype = 'image/jpeg'
        
        # Return the image as a file response with CORS headers
        response = send_file(image_binary, mimetype=mimetype)
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response
    except Exception as e:
        print(f"Error retrieving profile picture: {str(e)}")
        return jsonify({'error': str(e)}), 500

@user_bp.route('/test', methods=['GET'])
def test_endpoint():
    return jsonify({'message': 'Test endpoint is working!'}), 200 