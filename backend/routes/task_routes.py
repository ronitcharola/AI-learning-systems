from flask import Blueprint, request, jsonify
from bson.objectid import ObjectId
import datetime

from utils.db import get_db
from utils.auth_utils import token_required

task_bp = Blueprint('task_bp', __name__)

@task_bp.route('/add', methods=['POST'])
@token_required
def add_task(current_user):
    """Add a new task for the current user."""
    data = request.get_json()
    
    if not data or not data.get('title'):
        return jsonify({'message': 'Task title is required'}), 400
        
    db = get_db()
    
    task = {
        'user_id': current_user,
        'title': data.get('title'),
        'priority': data.get('priority', 'medium'), # low, medium, high
        'deadline': data.get('deadline'), # Expected format: ISO 8601 string
        'estimated_time': data.get('estimated_time', 30), # in minutes
        'actual_time': 0, # in minutes
        'status': data.get('status', 'pending'), # pending, in_progress, completed
        'created_at': datetime.datetime.utcnow()
    }
    
    result = db.tasks.insert_one(task)
    task['_id'] = str(result.inserted_id)
    
    return jsonify({
        'message': 'Task added successfully',
        'task': task
    }), 201

@task_bp.route('/get', methods=['GET'])
@token_required
def get_tasks(current_user):
    """Get all tasks for the current user."""
    db = get_db()
    
    tasks_cursor = db.tasks.find({'user_id': current_user})
    tasks = []
    
    for task in tasks_cursor:
        task['_id'] = str(task['_id'])
        tasks.append(task)
        
    return jsonify({'tasks': tasks}), 200

@task_bp.route('/update/<task_id>', methods=['PUT'])
@token_required
def update_task(current_user, task_id):
    """Update specific fields of an existing task."""
    data = request.get_json()
    db = get_db()
    
    if not data:
        return jsonify({'message': 'No data provided'}), 400
        
    try:
        obj_id = ObjectId(task_id)
    except:
        return jsonify({'message': 'Invalid task ID'}), 400
        
    update_data = {}
    allowed_fields = ['title', 'priority', 'deadline', 'estimated_time', 'actual_time', 'status']
    for field in allowed_fields:
        if field in data:
            update_data[field] = data[field]
            
    if not update_data:
        return jsonify({'message': 'No valid fields provided for update'}), 400
        
    result = db.tasks.update_one(
        {'_id': obj_id, 'user_id': current_user},
        {'$set': update_data}
    )
    
    if result.matched_count == 0:
        return jsonify({'message': 'Task not found or unauthorized'}), 404
        
    return jsonify({'message': 'Task updated successfully'}), 200

@task_bp.route('/delete/<task_id>', methods=['DELETE'])
@token_required
def delete_task(current_user, task_id):
    """Delete a task."""
    db = get_db()
    
    try:
        obj_id = ObjectId(task_id)
    except:
        return jsonify({'message': 'Invalid task ID'}), 400
        
    result = db.tasks.delete_one({'_id': obj_id, 'user_id': current_user})
    
    if result.deleted_count == 0:
        return jsonify({'message': 'Task not found or unauthorized'}), 404
        
    return jsonify({'message': 'Task deleted successfully'}), 200
