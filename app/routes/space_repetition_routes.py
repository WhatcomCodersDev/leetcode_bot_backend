# Routes that handle space repetition service, this includes user submissions
'''


'''
from datetime import datetime
from flask import Blueprint, request, jsonify
from app.services import fsrs_scheduler, submission_collection_manager, user_collection_manager, problem_manager
from app.services.util import handle_updating_submission_data

bp = Blueprint('space_repetition', __name__, url_prefix='/space_repetition')



# Deprecrate route/simplify 
# We only call this route for a new problem that hasn't been submitted before
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
    print(f'Handling problem submission for problem {problem_id}')
    data = request.json
    is_valid, validation_response = validate_request_data(problem_id, data)
    if not is_valid:
        return jsonify({'error': validation_response}), 400
    
    problem_data = validation_response
    
    try:
        # Get user UUID
        if data.get('discord_id'):
            user_uuid = user_collection_manager.get_uuid_from_discord_id(data['discord_id'])
        else:
            user_uuid = data['user_id']

        # First determine next time to review
        ## Only do if the problem doesn't exist in the submission collection
        previous_submission_doc = submission_collection_manager.get_user_submission_for_problem(user_uuid, problem_id).to_dict()
        if not previous_submission_doc:
            print("This problem hasn't beeen submitted before, so it should be scheduled for review")
            review_data = fsrs_scheduler.schedule_review(problem_id, 
                                                        datetime.now(), 
                                                        ease=2.5, 
                                                        interval=1, 
                                                        performance_rating=4) #todo pass user rating instead
            
            update_fields = handle_updating_submission_data(user_uuid, problem_id, data, review_data)
            
            # Update datastore
            submission_collection_manager.update_leetcode_submission(user_uuid,
                                                        problem_id, 
                                                        update_fields)
            
            if not review_data:
                print('No problem found')
                return jsonify({'error': 'No problem found'}), 404
        
            return jsonify(review_data), 200

    
    except ValueError:
        print('Invalid ID')
        return jsonify({'error': 'Invalid ID'}), 400

   
    return jsonify({'success': True}), 200
    

def validate_request_data(problem_id, data):
    """Validates the incoming request data.
    
    Args:
        problem_id (str): problem ID
        data (dict): request JSON data
    
    Returns:
        tuple: (bool, str) indicating success and error message if any
    """
    if not data:
        return False, 'No data provided'
    
    if not problem_id:
        return False, 'Problem ID not provided'
    
    problem_data = problem_manager.get_problem_by_id(int(problem_id))
    if not problem_data:
        return False, 'No problem found'
    
    if not data.get('discord_id') and not data.get('user_id'):
        return False, 'Discord ID or User ID not provided'
    
    return True, problem_data