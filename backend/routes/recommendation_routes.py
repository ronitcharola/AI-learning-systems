from flask import Blueprint, request, jsonify
from utils.db import get_db
from utils.auth_utils import token_required
from ml.predictor import ProductivityModel
import datetime

recommendation_bp = Blueprint('recommendation_bp', __name__)

# Initialize model (will load from disk or spin up synthetic if cold start)
model = ProductivityModel()

@recommendation_bp.route('/', methods=['GET'])
@token_required
def get_recommendations(current_user):
    """Provide smart suggestions using ML models."""
    db = get_db()
    tasks_cursor = db.tasks.find({'user_id': current_user, 'status': 'pending'})
    tasks = list(tasks_cursor)
    
    if not tasks:
        return jsonify({
            'next_task': None,
            'message': "You have no pending tasks. Great job!",
            'optimal_work_time': None,
            'warnings': []
        }), 200
        
    best_task = None
    highest_score = -1
    warnings = []
    
    for task in tasks:
        # Determine risk
        risk = model.predict_procrastination_risk(task.get('priority', 'medium'), past_delay=0)
        priority_val = {'high': 3, 'medium': 2, 'low': 1}.get(task.get('priority', 'medium'), 2)
        
        # Heuristic scoring: favor high priority items, penalize if risk is extremely high
        score = (priority_val * 100) - risk
        
        if score > highest_score:
            highest_score = score
            best_task = task
            
        if risk > 70:
            warnings.append(f"High procrastination risk for task: '{task.get('title')}'. Try breaking it down.")

    if best_task:
        best_task['_id'] = str(best_task['_id'])
        
    peak_hour = model.get_peak_productivity_hour()
    optimal_time = f"{peak_hour}:00 to {peak_hour+2}:00"
    
    # Assess burnout risk
    total_est = sum(t.get('estimated_time', 30) for t in tasks)
    if total_est > 480: # 8 hours
        warnings.append("Burnout Alert: You have over 8 hours of tasks pending today. Please consider rescheduling some.")
        
    return jsonify({
        'next_task': best_task,
        'optimal_work_time': optimal_time,
        'break_suggestions': "We recommend a 15-minute break after every 45 minutes of intense focus.",
        'warnings': list(set(warnings)) # remove dupes
    }), 200

@recommendation_bp.route('/ask', methods=['POST'])
@token_required
def ask_coach(current_user):
    """AI Coach Chatbot endpoint (Rule-based LLM mockup)"""
    data = request.get_json()
    if not data or 'question' not in data:
        return jsonify({'message': 'Please provide a question.'}), 400
        
    question = data.get('question', '').lower()
    
    # Simple rule-based mock responses for the AI Coach
    if 'productive' in question or 'when' in question:
        peak_hr = model.get_peak_productivity_hour()
        reply = f"Based on your past behavior, you are most productive around {peak_hr}:00. Try securing this time block for deep work and minimize distractions!"
    elif 'what should i do' in question or 'next' in question:
        reply = "I recommend checking your Recommendations tab. A good rule of thumb is to tackle your highest priority task first to build momentum."
    elif 'tired' in question or 'burnout' in question or 'sleepy' in question:
        reply = "It sounds like you might be exhausted. Remember to use the Pomodoro technique. It's okay to delay low-priority tasks to tomorrow and prioritize rest."
    else:
        reply = "That's a thoughtful question! As your AI Coach, my advice is to constantly break large tasks into smaller 20-minute chunks to maintain momentum."
        
    return jsonify({'reply': reply}), 200
