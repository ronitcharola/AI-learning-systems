from flask import Blueprint, jsonify
from utils.db import get_db
from utils.auth_utils import token_required
from ml.scheduler import generate_daily_schedule
import datetime

planner_bp = Blueprint('planner_bp', __name__)

@planner_bp.route('/generate', methods=['POST'])
@token_required
def generate_schedule(current_user):
    """Generate a daily schedule based on pending tasks."""
    db = get_db()
    
    # Fetch user's pending tasks
    tasks_cursor = db.tasks.find({
        'user_id': current_user,
        'status': 'pending'
    })
    
    tasks = list(tasks_cursor)
    
    if not tasks:
        return jsonify({'message': 'No pending tasks to schedule'}), 400
        
    # Generate schedule using our heuristic planner (soon to be AI-enhanced)
    schedule_items = generate_daily_schedule(tasks)
    
    today_str = datetime.datetime.now().strftime("%Y-%m-%d")
    
    schedule_doc = {
        'user_id': current_user,
        'date': today_str,
        'items': schedule_items,
        'created_at': datetime.datetime.utcnow()
    }
    
    # Save or update today's schedule in DB
    db.schedules.update_one(
        {'user_id': current_user, 'date': today_str},
        {'$set': schedule_doc},
        upsert=True
    )
    
    return jsonify({
        'message': 'Schedule generated successfully',
        'schedule': schedule_items
    }), 200

@planner_bp.route('/get', methods=['GET'])
@token_required
def get_schedule(current_user):
    """Get today's schedule."""
    db = get_db()
    today_str = datetime.datetime.now().strftime("%Y-%m-%d")
    
    schedule = db.schedules.find_one({'user_id': current_user, 'date': today_str})
    
    if not schedule:
        return jsonify({'message': 'No schedule generated for today', 'items': []}), 200
        
    schedule['_id'] = str(schedule['_id'])
    
    return jsonify({'schedule': schedule}), 200
