# Routes that handle space repetition service, this includes user submissions
'''


'''
from datetime import datetime
from flask import Blueprint, request, jsonify
from app.services import fsrs_scheduler, submission_collection_manager, user_collection_manager, problem_manager

bp = Blueprint('space_repetition', __name__, url_prefix='/space_repetition')

@bp.route('/<problem_id>/submit', methods=['POST'])
def handle_problem_submission(problem_id):
    '''Submit problem submission to space repetition service and update user's submission data

    Args:
        problem_id (str): problem ID
    
    Data:
        discord_id (str, optional): discord ID
        user_id (str, optional): user ID
        user_rating (int, optional): user rating
    
    Returns:
        dict: review data if successful, else error message
    
    '''
    data = request.json
    print(data)
    if not data:
        print('No data provided')
        return jsonify({'error': 'No data provided'}), 400
    
    if not problem_id:
        return jsonify({'error': 'Problem ID not provided'}), 400
    
    problem_data = problem_manager.get_problem_by_id(int(problem_id))
    
    if 'user_rating' not in data:
        user_rating = 3 #default    

    if not data.get('discord_id') and not data.get('user_id'):
        return jsonify({'error': 'Discord ID or User ID not provided'}), 400


    if not problem_id:
        print('ID not provided')
        return jsonify({'error': 'ID not provided'}), 400
    
    if 'attempted' not in data and 'solved' not in data:
        return jsonify({'error': 'Attempted or Solved not provided'}), 400

    try:
        # Get user UUID
        if data.get('discord_id'):
            user_uuid = user_collection_manager.get_uuid_from_discord_id(data['discord_id'])
        else:
            user_uuid = data['user_id']

        # First determine next time to review
        review_data = fsrs_scheduler.schedule_review(problem_id, 
                                                     datetime.now(), 
                                                     ease=2.5, 
                                                     interval=1, 
                                                     performance_rating=4) #todo pass user rating instead
        
        # Build submission data
        update_fields = {problem_id: {}}

        if 'user_rating' in data:
            update_fields[problem_id]['user_rating'] = user_rating
        
        if 'last_reviewed_timestamp' in data:
            update_fields[problem_id]['last_reviewed_timestamp'] = datetime.now()

        if 'next_review_timestamp' in data:
            update_fields[problem_id]['next_review_timestamp'] = review_data['next_review_timestamp']
        
        update_fields[problem_id]['category'] = problem_data.category
        
        # Update datastore
        submission_collection_manager.update_leetcode_submission(user_uuid,
                                                      problem_id, 
                                                      update_fields)
    
    except ValueError:
        print('Invalid ID')
        return jsonify({'error': 'Invalid ID'}), 400

    if not review_data:
        print('No problem found')
        return jsonify({'error': 'No problem found'}), 404
    
    return jsonify(review_data), 200

