
from flask import Blueprint, request, jsonify
from typing import List, Dict, Union
from app.services import user_problem_manager
from app.services import (
    firestore_user_collection_wrapper,
    firestore_leetcode_review_type_wrapper, 
    firestore_submission_collection_wrapper, 
    problem_manager
)
from app.services.user_submissions_reviewing.problem_to_review_data import ProblemToReview
from app.services.time_utils import handle_updating_submission_data, make_aware, make_naive, convert_dateime_now_to_pt
from app.routes.routes_utils import validate_request_data
from datetime import datetime

bp = Blueprint('users', __name__, url_prefix='/users')

@bp.route('/<user_id>', methods=['GET'])
def get_all_problems_for_user(user_id: str) -> Union[List[Dict[str, str]], int]:
    '''Api route to get all problems for a user

    Args:
        user_id (str): user id
    
    Returns:
        dict: problems for user if successfuly, else error message
    '''
    if not user_id:
        return jsonify({'error': 'ID not provided'}), 400


    try:
        problems = user_problem_manager.get_all_problems_for_user(user_id)
    except Exception as e:
        print(f"Error in get_all_problems_for_user for user {user_id}: {e}")
        return jsonify({'error': e}), 500
    
    if not problems:
        
        print('No problem found')
        return jsonify([{}])
    
    return jsonify(problems), 200

@bp.route('/<problem_id>/submit', methods=['POST'])
def add_problem_to_user_problems_for_review(problem_id: str) -> Union[Dict[str, str], int]:
    '''Api route that handles a user adding a problem to problem's they've already solved/seen before
    This amounts to adding a problem submission that could be used for future review
    
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
    is_valid = validate_request_data(problem_id, data) #use problem_id to get problem data
    if not is_valid:
        return jsonify({'error': 'Invalid data'}), 400
        
    problem_data = problem_manager.get_problem_by_id(int(problem_id))
    if not problem_data:
        return jsonify({'error': 'Problem not found'}), 404
        
    
    try:
        # Get user UUID
        if data.get('discord_id'):
            user_uuid = firestore_user_collection_wrapper.get_uuid_from_discord_id(data['discord_id'])
        else:
            user_uuid = data['user_id']


        ''' 3 cases when updating/adding a problem submission:

        1. User has never added a submission for this problem before
            We will add a new submission for this problem

        2. User has added a submission for this problem before
            Retrieve the previous submission and update the fields, but for now do nothing
        
        3. User is removing a submission for this problem
            Remove the submission for this problem
        '''

        # Case 3 - User is removing a submission for this problem
        if not problem_data:
            # TODO - explicitly remove submission from the database instead of setting it to empty
            update_fields = {problem_id: {}} #make the submission empty
            firestore_submission_collection_wrapper.update_leetcode_submission(
                user_uuid,
                problem_id, 
                update_fields,
            )
            return jsonify({'successful': update_fields}), 200
        
        # Retrieve the previous submission
        # The structure of problem_submissions is {problem_id: {problem_data}}
        previous_problem_data = None
        previous_problem_to_review = firestore_submission_collection_wrapper.get_user_submission_for_problem(
            user_uuid, 
            problem_id
            )
        print(f'previous_problem_to_review: {previous_problem_to_review.to_dict()}')
        
        if previous_problem_to_review:
            previous_problem_submission = previous_problem_to_review.to_dict()
        
        print(f'previous_problem_submission: {previous_problem_submission}')
        # If the dictionary exists, get the problem data by indexing the problem_id
        if previous_problem_submission and problem_id in previous_problem_submission:
            previous_problem_data = previous_problem_submission[problem_id]
        
        print(f'previous_problem_data: {previous_problem_data}')
        # Case 1 - User has added a submission for this problem before
        if previous_problem_data:
            print(f'User has previously added a submission for problem {problem_id}')
            print(f'Previous submission: {previous_problem_data}')
            #only update last_reviewed_timestamp
            previous_problem_data['last_reviewed_timestamp'] = convert_dateime_now_to_pt() 

            update_fields = ProblemToReview(
                problem_id=problem_id,
                category=problem_data.category,
                user_rating=previous_problem_data.get('user_rating', 3),
                last_reviewed_timestamp=previous_problem_data.get('last_reviewed_timestamp', None),
                next_review_timestamp=previous_problem_data.get('next_review_timestamp', None),
                streak=0
            ).to_dict()

            print(f'Updating submission: {update_fields}')
            firestore_submission_collection_wrapper.update_leetcode_submission(
                user_uuid,
                problem_id, 
                update_fields,
            )

            return jsonify({'successful': previous_problem_data}), 200
        
        # Case 2 - User has never added a submission for this problem before
        else:
            print(f'User has added a submission for problem {problem_id} before')
            update_fields = ProblemToReview(
                problem_id=problem_id,
                category=problem_data.category,
                streak=0
            ).to_dict()

            print(f'Adding new submission: {update_fields}')
            firestore_submission_collection_wrapper.update_leetcode_submission(
                user_uuid,
                problem_id, 
                update_fields,
            )
        
        
        return jsonify({'successful': update_fields}), 200

    
    except ValueError:
        print('Invalid ID')
        return jsonify({'error': 'Invalid ID'}), 400

    except Exception as e:
        print(f"Error in add_problem_to_user_problems_for_review for problem {problem_id}: {e}")
        return jsonify({'error': e}), 500
    


@bp.route('/<user_id>/problem/categories/review', methods=['GET'])
def get_problem_categories_marked_for_review(user_id) -> Union[Dict[str, str], int]:
    '''Api route to get all problem categories marked for review for a user
    
    Args:
        user_id (str): user id
    
    Returns:
        dict: review types for user if successful, else error message

    '''
    if not user_id:
        return jsonify({'error': 'ID not provided'}), 400

    try:
        review_types = firestore_leetcode_review_type_wrapper.get_problem_categories_marked_for_review_by_user(user_id)
    except Exception as e:
        print(f"Error in get_problem_categories_marked_for_review for user {user_id}: {e}")
        return jsonify({'error': e}), 500
    
    if not review_types:
        print('No review types found')
        return jsonify({})
        # return jsonify({'error': 'No review types found'}), 404
    
    return jsonify(review_types['review_types']), 200 #just return the list, its in the form of a key-value pair


@bp.route('/<user_id>/problem/categories/review/submit', methods=['POST'])
def mark_problem_categories_for_review(user_id: str) -> Union[Dict[str, str], int]:
    '''Api route to mark problem categories for review for a user
    
    Args:
        user_id (str): user id

    Data:
        category (list): list of problem categories marked for review by user


    Returns:
        dict: success message if successful, else error message
    
    '''
    data = request.json
    print(data)

    if not data:
        print('No data provided')
        return jsonify({'error': 'No data provided'}), 400
    
    if not user_id:
        return jsonify({'error': 'User ID not provided'}), 400
    
    if not data.get('category'):
        print('Problem category not provided')
        return jsonify({'error': 'Problem category not provided'}), 400

    try:
        firestore_leetcode_review_type_wrapper.update_user_problem_categories_marked_for_review(user_id, set(data['category']))
    except Exception as e:
        print(f"Error in mark_type_for_review for user {user_id}: {e}")
        return jsonify({'error': e}), 500
    
    return jsonify({'success': True}), 200

@bp.route('/<user_id>/review_problems/submit', methods=['POST'])
def update_review_problems_for_user(user_id: str) -> Union[Dict[str, str], int]:
    '''Api route to update review problems for a user
    
    Args:
        user_id (str): user id
    
    Data:
        Problems (List[Dict[str, str]]): List of problems with their review status and information
    
    Returns:
        dict: success message if successful, else error message
    '''
    data = request.json
    print("data:", data)

    if not data:
        print('No data provided')
        return jsonify({'error': 'No data provided'}), 400
    
    if not user_id:
        return jsonify({'error': 'User ID not provided'}), 400
    
    for problem_data in data:
        print("problem_data:", problem_data)
        print(type(problem_data["next_review_timestamp"]))
        print(list(problem_data.keys()))
        reference_problem_data = problem_manager.get_problem_by_id(int(problem_data["id"]))

        # Build submission data
        update_fields = {problem_data["id"]: {}}

        if 'user_rating' in problem_data and problem_data['user_rating'] != "" and int(problem_data['user_rating']) > 0:
            update_fields[problem_data["id"]]['user_rating'] = int(problem_data["user_rating"])
        # update_fields[problem_data["id"]]['category'] = problem_data["category"]
        
        if 'category' in problem_data:
            update_fields[problem_data["id"]]['category'] = reference_problem_data.category

        if 'last_reviewed_timestamp' in problem_data and len(problem_data['last_reviewed_timestamp']) > 0:
            try:
                update_fields[problem_data["id"]]['last_reviewed_timestamp'] = datetime.strptime(problem_data["last_reviewed_timestamp"], "%b %d, %Y, %I:%M:%S.%f %p")
            except ValueError:
                print("Invalid last_reviewed_timestamp format:", problem_data["last_reviewed_timestamp"])
                return jsonify({'error': 'Invalid last_reviewed_timestamp format'}), 400

        if 'next_review_timestamp' in problem_data and len(problem_data['next_review_timestamp']) > 0:
            try:
                update_fields[problem_data["id"]]['next_review_timestamp'] = datetime.strptime(problem_data["next_review_timestamp"], "%b %d, %Y, %I:%M:%S.%f %p")
            except ValueError:
                print("Invalid next_review_timestamp format:", problem_data["next_review_timestamp"])
                return jsonify({'error': 'Invalid next_review_timestamp format'}), 400


        print("update_fields:", update_fields)
        try:
            firestore_submission_collection_wrapper.update_leetcode_submission(user_id,
                                                      problem_data['id'], 
                                                      update_fields)
        except Exception as e:
            print(f"Error in mark_type_for_review for user {user_id}: {e}")
            return jsonify({'error': e}), 500
    
    return jsonify({'success': True}), 200