
from flask import Blueprint, request, jsonify
from typing import List, Dict, Union
from app.services import user_problem_manager
from app.services import (
    firestore_leetcode_review_type_wrapper, 
    firestore_submission_collection_wrapper, 
    problem_manager
)
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