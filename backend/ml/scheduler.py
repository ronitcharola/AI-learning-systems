import datetime

def generate_daily_schedule(tasks, start_hour=9, end_hour=17):
    """
    Generates a heuristic-based daily schedule.
    Prioritizes urgent and high-value tasks.
    Inserts breaks automatically.
    """
    # Priority mapping: higher number = higher priority
    priority_map = {'high': 3, 'medium': 2, 'low': 1}
    
    # Sort tasks: highest priority first. If same priority, shorter tasks first (Quick wins)
    sorted_tasks = sorted(
        tasks, 
        key=lambda x: (
            priority_map.get(x.get('priority', 'medium'), 2),
            -(x.get('estimated_time', 30)) # We'll do longer tasks first for High priority (Deep Work)
        ),
        reverse=True
    )
    
    schedule = []
    
    # We will plan for today
    today = datetime.datetime.now()
    current_time = today.replace(hour=start_hour, minute=0, second=0, microsecond=0)
    end_of_day = today.replace(hour=end_hour, minute=0, second=0, microsecond=0)
    
    # Fast forward if current time is already past start_hour
    if today > current_time and today < end_of_day:
        current_time = today
        # Round up to the next 15/30 minute mark for cleaner scheduling
        minutes_to_add = 15 - (current_time.minute % 15)
        current_time += datetime.timedelta(minutes=minutes_to_add)
        
    for task in sorted_tasks:
        est = task.get('estimated_time', 30)
        
        # Check if we have time left in the day
        if current_time + datetime.timedelta(minutes=est) > end_of_day:
            break # No more time to schedule tasks today
            
        schedule.append({
            'start_time': current_time.strftime("%H:%M"),
            'end_time': (current_time + datetime.timedelta(minutes=est)).strftime("%H:%M"),
            'type': 'task',
            'task_id': str(task.get('_id', '')),
            'title': task.get('title', 'Unknown Task'),
            'priority': task.get('priority', 'medium')
        })
        
        current_time += datetime.timedelta(minutes=est)
        
        # Add a 15 min break after a task if we haven't hit the end of the day, 
        # especially to avoid burnout after a Pomodoro session.
        if current_time + datetime.timedelta(minutes=15) <= end_of_day:
            schedule.append({
                'start_time': current_time.strftime("%H:%M"),
                'end_time': (current_time + datetime.timedelta(minutes=15)).strftime("%H:%M"),
                'type': 'break',
                'title': 'Break (Rest & Recharge)'
            })
            current_time += datetime.timedelta(minutes=15)

    return schedule
