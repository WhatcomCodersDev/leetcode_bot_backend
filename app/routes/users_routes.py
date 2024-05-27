
from flask import Blueprint, request, jsonify
from app.services import user_problem_manager

bp = Blueprint('users', __name__, url_prefix='/users')

@bp.route('/<user_id>', methods=['GET'])
def get_all_problems_for_user(user_id):
    if not user_id:
        return jsonify({'error': 'ID not provided'}), 400


    try:
        problems = user_problem_manager.get_all_problems_for_user(user_id)
        print("problems for user:", problems)
    except Exception as e:
        print(f"Error in get_all_problems_for_user for user {user_id}: {e}")
        return jsonify({'error': e}), 500
    
    if not problems:
        return jsonify({'error': 'No problem found'}), 404
    
    return jsonify(problems), 200

