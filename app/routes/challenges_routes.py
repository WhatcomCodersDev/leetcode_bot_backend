# Routes that handle user submitting answers to challenges
'''
1. Get a problem at random from spreadsheet based on difficulty
2. Get a problem based on id
3. Get a problem based on difficulty
4. Get a problem based on tag

'''

from flask import Blueprint, request, jsonify
from app.services import redis_client, leaderboard_manager, problem_manager
from constants import REDIS_ATTEMPTED_KEY, REDIS_SOLVED_KEY

bp = Blueprint('challenges', __name__, url_prefix='/challenges')


# Used by Leetcode bot to get a random problem of the week
@bp.route('/problem', methods=['GET'])
def get_problem():
    difficulty = request.args.get('difficulty')
    if not difficulty:
        return jsonify({'error': 'Difficulty not provided'}), 400
    
    if difficulty not in ['easy', 'medium', 'hard']:
        return jsonify({'error': 'Invalid difficulty'}), 400

    problem = problem_manager.get_problem(difficulty)
    if not problem:
        return jsonify({'error': 'No problem found'}), 404
    
    return jsonify(problem.to_dict()), 200

@bp.route('/user/<int:user_id>/<difficulty>/attempted', methods=['GET'])
def get_user_attempted(user_id, difficulty):
    if not user_id:
        return jsonify({'error': 'User ID not provided'}), 400
    
    if not difficulty:
        return jsonify({'error': 'Difficulty not provided'}), 400

    attempted = redis_client.check_if_user_has_attempted_problem(user_id, difficulty)
    return jsonify({'attempted': attempted}), 200

@bp.route('/user/<int:user_id>/<difficulty>/solved', methods=['GET'])
def get_user_submitted(user_id, difficulty):
    if not user_id:
        return jsonify({'error': 'User ID not provided'}), 400

    if not difficulty:
        return jsonify({'error': 'Difficulty not provided'}), 400
    
    submitted = redis_client.check_if_user_has_submitted_problem(user_id, difficulty)
    return jsonify({'submitted': submitted}), 200

@bp.route('/user/<int:user_id>/<difficulty>/attempt', methods=['POST'])
def process_user_attempt(user_id, difficulty):
    if not user_id or not difficulty:
        return jsonify({'error': 'User ID or difficulty not provided'}), 400
    
    try:
        points = leaderboard_manager.process_points_for_attempt(
            user_id=request.json.get('user_id'),
            difficulty=request.args.get('difficulty')
        )
    except Exception as e:
        return jsonify({'error': str(e)}), 400

    if not points:
        return jsonify({'error': 'No points given'}), 400
    
    return jsonify({'points': points}), 200

@bp.route('/user/<user_id>/<difficulty>/solved', methods=['POST'])
def process_user_submission(difficulty):
    if not request.json.get('user_id') or not request.json.get('difficulty'):
        return jsonify({'error': 'User ID or difficulty not provided'}), 400

    try:
        # Todo - This indirectly gets the problem from the cache, but it should be done directly
        problem_data = problem_manager.get_problem(difficulty) #TODO - fetch problem from cache?

        if not problem_data:
            return jsonify({'error': 'No problem found'}), 404

        points = leaderboard_manager.process_points_for_submission(
            question_id=problem_data.id,
            question_title=problem_data.name,
            user_id=request.json.get('user_id'),
            difficulty=request.args.get('difficulty')
        )
    except Exception as e:
        return jsonify({'error': str(e)}), 400

    if not points:
        return jsonify({'error': 'No points given'}), 400
    return jsonify({'points': points}), 200

