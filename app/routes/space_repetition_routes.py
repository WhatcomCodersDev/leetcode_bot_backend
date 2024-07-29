# Routes that handle space repetition service, this includes user submissions
'''


'''
from datetime import datetime, timedelta
from flask import Blueprint, request, jsonify
from app.services import fsrs_scheduler, firestore_submission_collection_wrapper, firestore_user_collection_wrapper, problem_manager, firestore_leetcode_review_type_wrapper
from app.services.time_utils import handle_updating_submission_data, make_aware, make_naive, convert_dateime_now_to_pt

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
            user_uuid = firestore_user_collection_wrapper.get_uuid_from_discord_id(data['discord_id'])
        else:
            user_uuid = data['user_id']

        print("problem_data:", problem_data)

        # First determine next time to review
        ## Only do if the problem doesn't exist in the submission collection
        previous_submission_doc = None
        previous_submission = firestore_submission_collection_wrapper.get_user_submission_for_problem(user_uuid, problem_id).to_dict()
        
        if previous_submission and problem_id in previous_submission:
            previous_submission_doc = previous_submission[problem_id]
        
        print("previous_submission_doc", previous_submission_doc)
        review_data = None
        if not previous_submission_doc  and problem_data.category != None:
            print("This problem hasn't beeen submitted before, so it should be scheduled for review")
            review_data = fsrs_scheduler.schedule_review(problem_id, 
                                                        datetime.now(), 
                                                        ease=1, 
                                                        interval=1, 
                                                        performance_rating=4) #todo pass user rating instead
            
            
            update_fields = handle_updating_submission_data(problem_id, data, review_data, problem_data)
           


        elif previous_submission_doc and 'next_review_timestamp' not in previous_submission_doc:
            print("This problem has beeen submitted before, but it doesn't have a next_review_timestamp")
            review_data = fsrs_scheduler.schedule_review(problem_id, 
                                                        convert_dateime_now_to_pt(), 
                                                        ease=1, 
                                                        interval=1, 
                                                        performance_rating=4) #todo pass user rating instead
            
            
            update_fields = handle_updating_submission_data(problem_id, data, review_data, problem_data)
           
        elif previous_submission_doc:
            print("This problem has beeen submitted before, and it has a next_review_timestamp")
            previous_submission_doc['last_reviewed_timestamp'] = convert_dateime_now_to_pt() #only update last_reviewed_timestamp

            update_fields = handle_updating_submission_data(problem_id, previous_submission_doc, review_data, problem_data)
            print("update_fields", update_fields)
        
        # Update datastore
        firestore_submission_collection_wrapper.update_leetcode_submission(user_uuid,
                                                problem_id, 
                                                update_fields)
        
        
        return jsonify({'successful': update_fields}), 200

    
    except ValueError:
        print('Invalid ID')
        return jsonify({'error': 'Invalid ID'}), 400

   
    return jsonify({'success': True}), 200
    

@bp.route('/daily_reminder', methods=['GET'])
def handle_daily_reminder():
    uuid_to_problems_id = firestore_submission_collection_wrapper.get_problem_past_reviewed_date()
    print("uuid_to_problems_id", uuid_to_problems_id)
    discord_id_to_problems = {}
    for uuid, problems_id in uuid_to_problems_id.items():
        user_review_categories = firestore_leetcode_review_type_wrapper.get_problem_categories_marked_for_review_by_user(uuid)
        
        if user_review_categories:
            user_review_categories = user_review_categories['review_types']

            print(uuid, problems_id)

            if len(problems_id) == 0:
                continue

            discord_id = firestore_user_collection_wrapper.get_discord_id_from_uuid(uuid)
            print(discord_id)
            discord_id_to_problems[discord_id] = []

            for prob_id in problems_id:
                prob_data = problem_manager.get_problem_by_id(int(prob_id))
                if prob_data.category in user_review_categories:
                    discord_id_to_problems[discord_id].append(prob_data)
    
    print(discord_id_to_problems)
    return jsonify({'discord_id_to_problems': discord_id_to_problems}), 200

@bp.route('/<uuid>/upcoming', methods=['GET'])
def get_upcoming_review_problems_for_user(uuid):
    '''Get upcoming review problems for a user
    
    Args:
        uuid (str): user ID
    
    Returns:
        dict: upcoming review problems for a user
    '''
    if not uuid:
        return jsonify({'error': 'User ID not provided'}), 400
    print(uuid)
  

    REVIEW_CATEGORY_KEY = 'review_types'
    user_problems = firestore_submission_collection_wrapper.get_user_submissions(uuid)
    user_review_categories = firestore_leetcode_review_type_wrapper.get_problem_categories_marked_for_review_by_user(uuid)[REVIEW_CATEGORY_KEY]

    # filter problems if they are in the review categories
    review_problems = []
    for problem_generator in user_problems:
        try:
            problem = problem_generator.to_dict()
            problem_id = problem_generator.id
            problem = next(iter(problem.values()))
            if 'category' in problem and problem['category'] in user_review_categories:
                # TODO - Also filter by date, this gets all review problems but we may
                # want to only get the review problems by the week

                # Augment problem data 
                problem_info = problem_manager.get_problem_by_id(int(problem_id))
                problem['id'] = problem_id
                problem['name'] = problem_info.name
                problem['link'] = problem_info.link

                # Figure out if it is in the review window
                # TODO - Bug - Fix date issues

             
                timewindow_in_memory = problem['next_review_timestamp'] + timedelta(days=2) # time window is 48 hours

        
                if problem['next_review_timestamp'] and (datetime.now() >= make_naive(problem['next_review_timestamp']) and datetime.now() < make_naive(timewindow_in_memory)) \
                                and (problem['last_reviewed_timestamp'] < problem['next_review_timestamp'] and problem['last_reviewed_timestamp'] < timewindow_in_memory):
                    problem['due'] = True

                review_problems.append(problem)
        except Exception as e:
            print(f"Error in get_all_problems_for_user for user {uuid}: {e}")
            continue
    
    
    return jsonify({'review_problems': review_problems}), 200



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
