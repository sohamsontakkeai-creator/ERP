"""
Authentication Routes Module
API endpoints for user authentication (login, registration, password reset, OAuth)
"""
from flask import Blueprint, request, jsonify, current_app
from flask_mail import Message
from models.user import User, UserStatus, db
from models.password_reset_token import PasswordResetToken
from werkzeug.security import check_password_hash, generate_password_hash
import threading
from threading import Thread
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/auth/register', methods=['POST'])
def register():
    """Register a new user with pending status"""
    try:
        data = request.get_json() or {}

        # Validate required fields
        required_fields = ['full_name', 'email', 'username', 'password', 'department']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400

        # Check if email already exists
        if User.query.filter_by(email=data['email']).first():
            return jsonify({'error': 'Email already registered'}), 409

        # Check if username already exists
        if User.query.filter_by(username=data['username']).first():
            return jsonify({'error': 'Username already taken'}), 409

        # Create new user with pending status
        new_user = User(
            full_name=data['full_name'],
            email=data['email'],
            username=data['username'],
            department=data['department'],
            status=UserStatus.PENDING
        )
        new_user.set_password(data['password'])

        db.session.add(new_user)
        db.session.commit()

        return jsonify({
            'message': 'Registration successful! Your account is pending approval.',
            'user': new_user.to_dict()
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/auth/login', methods=['POST'])
def login():
    """Authenticate a user using either username or email and return user data"""
    try:
        data = request.get_json() or {}

        # Validate required fields
        if ('username' not in data and 'email' not in data) or 'password' not in data:
            return jsonify({'error': 'Username/Email and password are required'}), 400

        # Find user by username or email
        if 'username' in data:
            user = User.query.filter_by(username=data['username']).first()
        else:
            user = User.query.filter_by(email=data['email']).first()

        # Check if user exists and password is correct
        if not user or not user.check_password(data['password']):
            return jsonify({'error': 'Invalid credentials'}), 401

        # Check if user is approved
        if user.status != UserStatus.APPROVED:
            return jsonify({'error': 'Your account is pending approval', 'status': user.status.value}), 403

        # Return user data
        return jsonify({
            'message': 'Login successful',
            'user': user.to_dict()
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/auth/pending-users', methods=['GET'])
def get_pending_users():
    """Get all users with pending status (admin only)"""
    try:
        # TODO: Add admin authentication check

        pending_users = User.query.filter_by(status=UserStatus.PENDING).all()
        return jsonify([user.to_dict() for user in pending_users]), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/auth/approve-user/<int:user_id>', methods=['PUT'])
def approve_user(user_id):
    """Approve a pending user (admin only)"""
    try:
        # TODO: Add admin authentication check

        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404

        if user.status != UserStatus.PENDING:
            return jsonify({'error': 'User is not in pending status'}), 400

        user.status = UserStatus.APPROVED
        db.session.commit()

        return jsonify({
            'message': 'User approved successfully',
            'user': user.to_dict()
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/auth/reject-user/<int:user_id>', methods=['PUT'])
def reject_user(user_id):
    """Reject a pending user (admin only)"""
    try:
        # TODO: Add admin authentication check

        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404

        if user.status != UserStatus.PENDING:
            return jsonify({'error': 'User is not in pending status'}), 400

        user.status = UserStatus.REJECTED
        db.session.commit()

        return jsonify({
            'message': 'User rejected successfully',
            'user': user.to_dict()
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/auth/users', methods=['GET'])
def get_all_users():
    """Get all users (admin only)"""
    try:
        # TODO: Add admin authentication check

        users = User.query.all()
        return jsonify([user.to_dict() for user in users]), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/auth/users/<int:user_id>/department', methods=['PUT'])
def update_user_department(user_id):
    """Update user's department (admin only)"""
    try:
        # TODO: Add admin authentication check

        data = request.get_json() or {}

        if 'department' not in data:
            return jsonify({'error': 'Department is required'}), 400

        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404

        user.department = data['department']
        db.session.commit()

        return jsonify({
            'message': 'User department updated successfully',
            'user': user.to_dict()
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/auth/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    """Delete a user from the system (admin only)"""
    try:
        # TODO: Add admin authentication check

        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404

        # Prevent admin from deleting themselves
        if user.department == 'admin':
            return jsonify({'error': 'Cannot delete admin user'}), 400

        db.session.delete(user)
        db.session.commit()

        return jsonify({
            'message': 'User deleted successfully'
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/auth/forgot-password', methods=['POST'])
def forgot_password():
    try:
        data = request.get_json() or {}
        if 'email' not in data:
            return jsonify({'error': 'Email is required'}), 400

        user = User.query.filter_by(email=data['email']).first()
        if not user:
            return jsonify({'error': 'No account found with this email'}), 404

        reset_token_obj = PasswordResetToken.create_token(user.id)
        frontend_base_url = current_app.config.get('FRONTEND_BASE_URL', 'http://localhost:5173')
        reset_url = f"{frontend_base_url}/reset-password?token={reset_token_obj.token}"

        # Send email using SendGrid in a background thread
        def send_email(user_email, reset_url):
            message = Mail(
                from_email=current_app.config['MAIL_DEFAULT_SENDER'],
                to_emails=user_email,
                subject='Password Reset Request',
                html_content=f"""
                    <p>Hi,</p>
                    <p>Click the link below to reset your password:</p>
                    <a href="{reset_url}">{reset_url}</a>
                    <p>If you did not request this, please ignore this email.</p>
                """
            )
            try:
                sg = SendGridAPIClient(current_app.config['SENDGRID_API_KEY'])
                response = sg.send(message)
                print(f"✅ Reset email sent to {user_email}. Status code: {response.status_code}")
            except Exception as e:
                print(f"❌ Failed to send email: {e}")

        Thread(target=send_email, args=(user.email, reset_url)).start()

        return jsonify({
            'message': 'A reset link has been sent to your email address.',
            'reset_token': reset_token_obj.token,
            'reset_url': reset_url
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
        
@auth_bp.route('/auth/reset-password', methods=['POST'])
def reset_password():
    """Reset user password using token"""
    try:
        data = request.get_json() or {}

        required_fields = ['token', 'new_password']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400

        # Validate token and get user
        user = PasswordResetToken.validate_token(data['token'])
        if not user:
            return jsonify({'error': 'Invalid or expired reset token'}), 400

        # Update password
        user.set_password(data['new_password'])
        db.session.commit()

        # Mark token as used
        PasswordResetToken.mark_token_used(data['token'])

        return jsonify({'message': 'Password reset successfully'}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/auth/departments', methods=['GET'])
def get_departments():
    """Get all available departments"""
    try:
        # Default departments
        default_departments = ['production', 'purchase', 'store', 'assembly', 'finance', 'showroom', 'sales', 'dispatch', 'transport', 'hr', 'watchman', 'admin']

        # Get unique departments from existing users
        users = User.query.all()
        user_departments = set(user.department for user in users if user.department)

        # Combine and sort
        all_departments = sorted(list(set(default_departments + list(user_departments))))

        return jsonify({'departments': all_departments}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


