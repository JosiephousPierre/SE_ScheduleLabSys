from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, verify_jwt_in_request
from models import User, Notification
from extensions import db
from functools import wraps

notification_bp = Blueprint('notifications', __name__)

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

@notification_bp.route('/', methods=['GET'])
@jwt_required_custom
def get_user_notifications():
    current_user_id = get_jwt_identity()
    
    # Get query parameters
    is_read = request.args.get('is_read')
    
    # Start with base query
    query = Notification.query.filter_by(user_id=current_user_id)
    
    # Apply filters if provided
    if is_read is not None:
        is_read_bool = is_read.lower() == 'true'
        query = query.filter_by(is_read=is_read_bool)
    
    # Order by created_at (newest first)
    query = query.order_by(Notification.created_at.desc())
    
    # Execute query
    notifications = query.all()
    
    return jsonify([notification.to_dict() for notification in notifications]), 200

@notification_bp.route('/<int:notification_id>', methods=['GET'])
@jwt_required_custom
def get_notification(notification_id):
    current_user_id = get_jwt_identity()
    
    notification = Notification.query.get(notification_id)
    
    if not notification:
        return jsonify({'error': 'Notification not found'}), 404
    
    # Check if notification belongs to current user
    if notification.user_id != current_user_id:
        return jsonify({'error': 'Unauthorized to view this notification'}), 403
    
    return jsonify(notification.to_dict()), 200

@notification_bp.route('/<int:notification_id>/read', methods=['PUT'])
@jwt_required_custom
def mark_notification_as_read(notification_id):
    current_user_id = get_jwt_identity()
    
    notification = Notification.query.get(notification_id)
    
    if not notification:
        return jsonify({'error': 'Notification not found'}), 404
    
    # Check if notification belongs to current user
    if notification.user_id != current_user_id:
        return jsonify({'error': 'Unauthorized to update this notification'}), 403
    
    notification.is_read = True
    db.session.commit()
    
    return jsonify({
        'message': 'Notification marked as read',
        'notification': notification.to_dict()
    }), 200

@notification_bp.route('/read-all', methods=['PUT'])
@jwt_required_custom
def mark_all_notifications_as_read():
    current_user_id = get_jwt_identity()
    
    # Get all unread notifications for current user
    unread_notifications = Notification.query.filter_by(
        user_id=current_user_id,
        is_read=False
    ).all()
    
    # Mark all as read
    for notification in unread_notifications:
        notification.is_read = True
    
    db.session.commit()
    
    return jsonify({
        'message': f'Marked {len(unread_notifications)} notifications as read'
    }), 200

@notification_bp.route('/<int:notification_id>', methods=['DELETE'])
@jwt_required_custom
def delete_notification(notification_id):
    current_user_id = get_jwt_identity()
    
    notification = Notification.query.get(notification_id)
    
    if not notification:
        return jsonify({'error': 'Notification not found'}), 404
    
    # Check if notification belongs to current user
    if notification.user_id != current_user_id:
        return jsonify({'error': 'Unauthorized to delete this notification'}), 403
    
    db.session.delete(notification)
    db.session.commit()
    
    return jsonify({'message': 'Notification deleted successfully'}), 200

@notification_bp.route('/delete-all', methods=['DELETE'])
@jwt_required_custom
def delete_all_notifications():
    current_user_id = get_jwt_identity()
    
    # Get all notifications for current user
    notifications = Notification.query.filter_by(user_id=current_user_id).all()
    
    # Delete all
    for notification in notifications:
        db.session.delete(notification)
    
    db.session.commit()
    
    return jsonify({
        'message': f'Deleted {len(notifications)} notifications'
    }), 200

@notification_bp.route('/count', methods=['GET'])
@jwt_required_custom
def get_notification_count():
    current_user_id = get_jwt_identity()
    
    # Count unread notifications
    unread_count = Notification.query.filter_by(
        user_id=current_user_id,
        is_read=False
    ).count()
    
    # Count total notifications
    total_count = Notification.query.filter_by(
        user_id=current_user_id
    ).count()
    
    return jsonify({
        'unread_count': unread_count,
        'total_count': total_count
    }), 200 