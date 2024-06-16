
from flask import Blueprint, request, jsonify
from app.services import user_problem_manager
from app.services import leetcode_review_type_manager, submission_manager


bp = Blueprint('users', __name__, url_prefix='/users')

@bp.route('/<user_id>', methods=['GET'])
def get_all_problems_for_user(user_id):
    if not user_id:
        return jsonify({'error': 'ID not provided'}), 400


    try:
        problems = user_problem_manager.get_all_problems_for_user(user_id)
        # print("problems for user:", problems)
    except Exception as e:
        print(f"Error in get_all_problems_for_user for user {user_id}: {e}")
        return jsonify({'error': e}), 500
    
    if not problems:
        print('No problem found')
        return jsonify({})
        # return jsonify({'error': 'No problem found'}), 404
    
    return jsonify(problems), 200

@bp.route('/<user_id>/problem/categories/review', methods=['GET'])
def get_problem_categories_marked_for_review(user_id):
    if not user_id:
        return jsonify({'error': 'ID not provided'}), 400

    try:
        review_types = leetcode_review_type_manager.get_user_review_types(user_id)
    except Exception as e:
        print(f"Error in get_problem_categories_marked_for_review for user {user_id}: {e}")
        return jsonify({'error': e}), 500
    
    if not review_types:
        print('No review types found')
        return jsonify({})
        # return jsonify({'error': 'No review types found'}), 404
    
    return jsonify(review_types['review_types']), 200 #just return the list, its in the form of a key-value pair


@bp.route('/<user_id>/problem/categories/review/submit', methods=['POST'])
def mark_problem_categories_for_review(user_id):
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
        leetcode_review_type_manager.update_user_review_types(user_id, set(data['category']))
    except Exception as e:
        print(f"Error in mark_type_for_review for user {user_id}: {e}")
        return jsonify({'error': e}), 500
    
    return jsonify({'success': True}), 200

@bp.route('/<user_id>/review_problems/submit', methods=['POST'])
def update_review_problems_for_user(user_id):
    data = request.json
    print("data:", data)

    if not data:
        print('No data provided')
        return jsonify({'error': 'No data provided'}), 400
    
    if not user_id:
        return jsonify({'error': 'User ID not provided'}), 400
    
    for problem_data in data:
        try:
            submission_manager.update_leetcode_submission(user_id,
                                                      problem_data['id'], 
                                                      problem_data)
        except Exception as e:
            print(f"Error in mark_type_for_review for user {user_id}: {e}")
            return jsonify({'error': e}), 500
    
    return jsonify({'success': True}), 200