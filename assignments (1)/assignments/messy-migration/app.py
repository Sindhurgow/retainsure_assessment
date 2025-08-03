from flask import Flask, request, jsonify, abort
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.exceptions import HTTPException
import os
import logging
from datetime import datetime
import re

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Configuration
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your-secret-key-change-in-production')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///users.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize SQLAlchemy
db = SQLAlchemy(app)

# User Model
class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        """Return user data as dictionary (excluding password)"""
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

# Validation functions
def validate_email(email):
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_password(password):
    """Validate password strength"""
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    return True, ""

def validate_name(name):
    """Validate name format"""
    if not name or len(name.strip()) < 2:
        return False, "Name must be at least 2 characters long"
    return True, ""

# Error handlers
@app.errorhandler(HTTPException)
def handle_http_error(error):
    """Handle HTTP errors"""
    return jsonify({
        'error': error.description,
        'status_code': error.code
    }), error.code

@app.errorhandler(Exception)
def handle_generic_error(error):
    """Handle generic errors"""
    logger.error(f"Unhandled error: {str(error)}")
    return jsonify({
        'error': 'Internal server error',
        'status_code': 500
    }), 500

# Routes
@app.route('/')
def home():
    """Health check endpoint"""
    return jsonify({
        'message': 'User Management System',
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat()
    })

@app.route('/users', methods=['GET'])
def get_all_users():
    """Get all users (excluding passwords)"""
    try:
        users = User.query.all()
        return jsonify({
            'users': [user.to_dict() for user in users],
            'count': len(users)
        })
    except Exception as e:
        logger.error(f"Error fetching users: {str(e)}")
        abort(500)

@app.route('/user/<int:user_id>', methods=['GET'])
def get_user(user_id):
    """Get specific user by ID"""
    try:
        user = User.query.get(user_id)
        if not user:
            abort(404, description="User not found")
        
        return jsonify(user.to_dict())
    except Exception as e:
        logger.error(f"Error fetching user {user_id}: {str(e)}")
        abort(500)

@app.route('/users', methods=['POST'])
def create_user():
    """Create a new user"""
    try:
        data = request.get_json()
        if not data:
            abort(400, description="Invalid JSON data")
        
        # Extract and validate data
        name = data.get('name', '').strip()
        email = data.get('email', '').strip()
        password = data.get('password', '')
        
        # Validate required fields
        if not name or not email or not password:
            abort(400, description="Name, email, and password are required")
        
        # Validate name
        name_valid, name_error = validate_name(name)
        if not name_valid:
            abort(400, description=name_error)
        
        # Validate email
        if not validate_email(email):
            abort(400, description="Invalid email format")
        
        # Validate password
        password_valid, password_error = validate_password(password)
        if not password_valid:
            abort(400, description=password_error)
        
        # Check if email already exists
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            abort(409, description="Email already registered")
        
        # Create new user
        password_hash = generate_password_hash(password)
        new_user = User(name=name, email=email, password_hash=password_hash)
        
        db.session.add(new_user)
        db.session.commit()
        
        logger.info(f"User created successfully: {email}")
        return jsonify({
            'message': 'User created successfully',
            'user': new_user.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error creating user: {str(e)}")
        abort(500)

@app.route('/user/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    """Update user information"""
    try:
        user = User.query.get(user_id)
        if not user:
            abort(404, description="User not found")
        
        data = request.get_json()
        if not data:
            abort(400, description="Invalid JSON data")
        
        # Update fields if provided
        if 'name' in data:
            name = data['name'].strip()
            name_valid, name_error = validate_name(name)
            if not name_valid:
                abort(400, description=name_error)
            user.name = name
        
        if 'email' in data:
            email = data['email'].strip()
            if not validate_email(email):
                abort(400, description="Invalid email format")
            
            # Check if email is already taken by another user
            existing_user = User.query.filter_by(email=email).first()
            if existing_user and existing_user.id != user_id:
                abort(409, description="Email already registered")
            user.email = email
        
        user.updated_at = datetime.utcnow()
        db.session.commit()
        
        logger.info(f"User {user_id} updated successfully")
        return jsonify({
            'message': 'User updated successfully',
            'user': user.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error updating user {user_id}: {str(e)}")
        abort(500)

@app.route('/user/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    """Delete a user"""
    try:
        user = User.query.get(user_id)
        if not user:
            abort(404, description="User not found")
        
        db.session.delete(user)
        db.session.commit()
        
        logger.info(f"User {user_id} deleted successfully")
        return jsonify({
            'message': 'User deleted successfully'
        })
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error deleting user {user_id}: {str(e)}")
        abort(500)

@app.route('/search', methods=['GET'])
def search_users():
    """Search users by name"""
    try:
        name = request.args.get('name', '').strip()
        if not name:
            abort(400, description="Please provide a name to search")
        
        # Use case-insensitive search
        users = User.query.filter(User.name.ilike(f'%{name}%')).all()
        
        return jsonify({
            'users': [user.to_dict() for user in users],
            'count': len(users),
            'search_term': name
        })
        
    except Exception as e:
        logger.error(f"Error searching users: {str(e)}")
        abort(500)

@app.route('/login', methods=['POST'])
def login():
    """User login"""
    try:
        data = request.get_json()
        if not data:
            abort(400, description="Invalid JSON data")
        
        email = data.get('email', '').strip()
        password = data.get('password', '')
        
        if not email or not password:
            abort(400, description="Email and password are required")
        
        # Find user by email
        user = User.query.filter_by(email=email).first()
        
        if user and check_password_hash(user.password_hash, password):
            logger.info(f"Successful login for user: {email}")
            return jsonify({
                'status': 'success',
                'message': 'Login successful',
                'user': user.to_dict()
            })
        else:
            logger.warning(f"Failed login attempt for email: {email}")
            return jsonify({
                'status': 'failed',
                'message': 'Invalid email or password'
            }), 401
            
    except Exception as e:
        logger.error(f"Error during login: {str(e)}")
        abort(500)

# Database initialization
def init_db():
    """Initialize the database"""
    with app.app_context():
        db.create_all()
        logger.info("Database initialized successfully")

if __name__ == '__main__':
    # Initialize database
    init_db()
    
    # Run the application
    debug_mode = os.environ.get('FLASK_ENV') == 'development'
    app.run(
        host='0.0.0.0', 
        port=int(os.environ.get('PORT', 5000)),
        debug=debug_mode
    )