from flask import Blueprint, jsonify
from utils.db import get_db
from utils.auth_utils import token_required

insights_bp = Blueprint('insights_bp', __name__)

@insights_bp.route('/', methods=['GET'])
@token_required
def get_insights(current_user):
    """Retrieve productivity score and stats for dashboard reporting."""
    db = get_db()
    tasks_cursor = db.tasks.find({'user_id': current_user})
    tasks = list(tasks_cursor)
    
    total_tasks = len(tasks)
    completed_tasks = len([t for t in tasks if t.get('status') == 'completed'])
    
    completion_rate = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
    productivity_score = int(completion_rate) 
    
    total_focus_minutes = sum(t.get('actual_time', 0) for t in tasks if t.get('status') == 'completed')
    focus_hours = round(total_focus_minutes / 60, 1)
    
    # Mock trend data for chart rendering in frontend
    trends = [
        {'day': 'Mon', 'score': 60},
        {'day': 'Tue', 'score': 75},
        {'day': 'Wed', 'score': 80},
        {'day': 'Thu', 'score': 90},
        {'day': 'Fri', 'score': productivity_score if productivity_score > 0 else 50}
    ]
    
    return jsonify({
        'productivity_score': productivity_score,
        'focus_hours': focus_hours,
        'completion_rate': round(completion_rate, 1),
        'total_tasks': total_tasks,
        'completed_tasks': completed_tasks,
        'trends': trends
    }), 200
