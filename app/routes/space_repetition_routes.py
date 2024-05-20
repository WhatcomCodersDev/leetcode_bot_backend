# Routes that handle space repetition
'''


'''
from datetime import datetime
from flask import Blueprint, request, jsonify
from app.services import fsrs_scheduler, submission_manager, user_manager

bp = Blueprint('space_repetition', __name__, url_prefix='/space_repetition')

@bp.route('/<problem_id>/submit', methods=['POST'])
def handle_problem_submission(problem_id):
    data = request.json
    print(data)
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    if not data.get('discord_id') or not data.get('user_id'):
        return jsonify({'error': 'discord id or user_id not provided'}), 400
    
    if not data.get('difficulty'):
        return jsonify({'error': 'User ID or difficulty not provided'}), 400
    
    if 'attempted' not in data or 'solved' not in data:
        return jsonify({'error': 'Attempted or solved not provided'}), 400

    if not problem_id:
        return jsonify({'error': 'ID not provided'}), 400
    
    try:
        # Get user UUID
        if data.get('discord_id'):
            user_uuid = user_manager.get_uuid_from_discord_id(data['discord_id'])
        else:
            user_uuid = data['user_id']

        # First determine next time to review
        review_data = fsrs_scheduler.schedule_review(problem_id, 
                                                     datetime.now(), 
                                                     ease=2.5, 
                                                     interval=1, 
                                                     performance_rating=4)
        
        # Build submission data
        update_fields = {problem_id: {}}
        update_fields[problem_id]['difficulty'] = data.get('difficulty')
        
        if data.get('solved'):
            update_fields[problem_id]['solved_timestamp'] = datetime.now()
        
        if data.get('attempted'):
            update_fields[problem_id]['attempted_timestamp'] = datetime.now()
        
        update_fields[problem_id]['next_review_date'] = review_data['next_review_date']
        
        # Update datastore
        submission_manager.update_leetcode_submission(user_uuid,
                                                      problem_id, 
                                                      update_fields)
    
    except ValueError:
        return jsonify({'error': 'Invalid ID'}), 400

    if not review_data:
        return jsonify({'error': 'No problem found'}), 404
    
    return jsonify(review_data), 200

