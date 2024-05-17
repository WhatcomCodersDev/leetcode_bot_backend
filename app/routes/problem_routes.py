# Routes that handle fetching problems
'''
1. Get a problem at random from spreadsheet based on difficulty
2. Get a problem based on id
3. Get a problem based on difficulty
4. Get a problem based on tag

'''
from flask import Blueprint, request, jsonify
from app.services import problem_manager, firestore_wrapper
from datetime import datetime

bp = Blueprint('problems', __name__, url_prefix='/problems')

@bp.route('/<problem_id>', methods=['GET'])
def get_problem_by_id(problem_id):
    if not problem_id:
        return jsonify({'error': 'ID not provided'}), 400
    
    try:
        problem_id = int(problem_id)
    except ValueError:
        return jsonify({'error': 'Invalid ID'}), 400

    try:
        problem = problem_manager.get_problem_by_id(problem_id)
    except Exception as e:
        print(e) #todo fix this later
        return jsonify({f'error: No problem found'}), 400

    return jsonify(problem), 200

# Used by Leetcode bot to set a problem as solved
@bp.route('/<int:problem_id>/solved', methods=['PUT'])
def mark_problem_solved(problem_id):
    if not problem_id:
        return jsonify({'error': 'Problem ID not provided'}), 400

    success = firestore_wrapper.update_last_asked_timestamp(problem_id, datetime.now())

    if not success:
        return jsonify({'error': f'Cannot mark {problem_id} as solved'}), 400
    
    return jsonify({'message': f'Marked {problem_id} as solved'}), 200


# Used by Leetcode bot to get a random problem as per user request
@bp.route('/<difficulty>/request', methods=['GET'])
def get_problem_user_request(difficulty):
    if not difficulty:
        return jsonify({'error': 'Difficulty not provided'}), 400
    
    if difficulty not in ['easy', 'medium', 'hard']:
        return jsonify({'error': 'Invalid difficulty'}), 400

    # select_problem_at_random() = no cache
    problem = problem_manager.select_problem_at_random(difficulty)
    if not problem:
        return jsonify({'error': 'No problem found'}), 404
    
    return jsonify(problem), 200

