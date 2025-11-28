from flask import Blueprint, request, jsonify
import bcrypt
import jwt
from werkzeug.utils import secure_filename
import os
import pathlib

auth_bp = Blueprint('auth', __name__)

# TODO: Use a database instead of in-memory storage
users = []

next_id = 1

def get_next_id():
    global next_id
    current = next_id
    next_id += 1
    return current

@auth_bp.after_request
def after_request(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Origin, X-Requested-With, Content-Type, Accept, Authorization'
    return response


@auth_bp.route('/users', methods=['POST'])
def create_user():
    try:
        data = request.get_json()
        name = data.get('name')
        email = data.get('email')
        password = data.get('password')
        
        existing_user = next((user for user in users if user['email'] == email), None)
        if existing_user:
            return jsonify({'error': 'User already exists'}), 400
        
        user = {
            'id': get_next_id(),
            'name': name,
            'email': email,
            'password': password,
        }
        
        users.append(user)
        
        return jsonify(user), 201
    except Exception as error:
        return jsonify({'error': str(error)}), 500

@auth_bp.route('/users/search', methods=['GET'])
def search_users():
    try:
        q = request.args.get('q')
        limit = request.args.get('limit')
        offset = request.args.get('offset')
        
        filtered_users = users
        
        if q:
            filtered_users = [user for user in users if user['name'] == q or user['email'] == q]
        
        return jsonify({
            'users': filtered_users,
            'total': len(filtered_users),
        })
    except Exception as error:
        return jsonify({'error': str(error)}), 500


@auth_bp.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')
        
        user = next((u for u in users if u['email'] == email), None)
        if not user:
            return jsonify({'error': 'Invalid credentials'}), 401
        
        is_valid_password = bcrypt.checkpw(password.encode('utf-8'), user['password'].encode('utf-8'))
        if not is_valid_password:
            return jsonify({'error': 'Invalid credentials'}), 401
        
        token = jwt.encode(
            {'userId': user['id'], 'email': user['email']},
            'secret',
            algorithm='HS256'
        )
        
        return jsonify({
            'token': token,
            'user': {
                'id': user['id'],
                'name': user['name'],
                'email': user['email'],
                'avatar': user.get('avatar')
            }
        })
    except Exception as error:
        return jsonify({'error': str(error)}), 500

@auth_bp.route('/users/<id>', methods=['GET'])
def get_user(id):
    try:
        user_id = int(id)
        
        user = next((u for u in users if u['id'] == user_id), None)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        return jsonify(user)
    except Exception as error:
        return jsonify({'error': str(error)}), 500

@auth_bp.route('/users/<id>', methods=['DELETE'])
def delete_user(id):
    try:
        user_id = int(id)
        
        user_index = next((i for i, u in enumerate(users) if u['id'] == user_id), None)
        if user_index is None:
            return jsonify({'error': 'User not found'}), 404
        
        users.pop(user_index)
        
        return jsonify({'message': 'User deleted successfully'})
    except Exception as error:
        return jsonify({'error': str(error)}), 500

