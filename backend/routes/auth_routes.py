from flask import Blueprint, request, jsonify
from utils.db import get_db
from utils.auth_utils import hash_password, check_password, generate_token

auth_bp = Blueprint('auth_bp', __name__)

@auth_bp.route('/signup', methods=['POST'])
def signup():
    """Register a new user."""
    data = request.get_json()
    
    if not data or not data.get('email') or not data.get('password'):
        return jsonify({'message': 'Missing required fields (email, password)'}), 400
        
    db = get_db()
    users_collection = db.users
    
    # Check if user already exists
    if users_collection.find_one({'email': data['email']}):
        return jsonify({'message': 'User already exists'}), 409
        
    hashed_password = hash_password(data['password'])
    
    user = {
        'email': data['email'],
        'password': hashed_password,
        'name': data.get('name', '')
    }
    
    result = users_collection.insert_one(user)
    
    return jsonify({
        'message': 'User created successfully',
        'user_id': str(result.inserted_id)
    }), 201

@auth_bp.route('/login', methods=['POST'])
def login():
    """Log in an existing user and return a JWT."""
    data = request.get_json()
    
    if not data or not data.get('email') or not data.get('password'):
        return jsonify({'message': 'Missing required fields (email, password)'}), 400
        
    db = get_db()
    user = db.users.find_one({'email': data['email']})
    
    if not user:
        return jsonify({'message': 'Invalid credentials'}), 401
        
    if check_password(data['password'], user['password']):
        token = generate_token(str(user['_id']))
        return jsonify({
            'message': 'Login successful',
            'token': token,
            'user': {
                'id': str(user['_id']),
                'email': user['email'],
                'name': user.get('name', '')
            }
        }), 200
        
    return jsonify({'message': 'Invalid credentials'}), 401
