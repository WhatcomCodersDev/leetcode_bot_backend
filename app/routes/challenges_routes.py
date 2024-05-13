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
    
    return jsonify(problem), 200

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

@bp.route('/user/attempt', methods=['POST'])
def process_user_attempt():
    data = request.json
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    if not data.get('user_id') or not data.get('difficulty'):
        return jsonify({'error': 'User ID or difficulty not provided'}), 400
    user_id = data['user_id']
    difficulty = data['difficulty']

    try:
        points = leaderboard_manager.process_points_for_attempt(
            user_id=user_id,
            difficulty=difficulty
        )
    except Exception as e:
        return jsonify({'error': str(e)}), 400

    if not points:
        return jsonify({'error': 'No points given'}), 400
    
    return jsonify({'points': points}), 200

@bp.route('/user/solved', methods=['POST'])
def process_user_submission():
    data = request.json
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    if not data.get('user_id') or not data.get('difficulty'):
        return jsonify({'error': 'User ID or difficulty not provided'}), 400

    user_id = data['user_id']
    difficulty = data['difficulty']

    try:
        # Todo - This indirectly gets the problem from the cache, but it should be done directly
        problem_data = problem_manager.get_problem(difficulty) #TODO - fetch problem from cache?

        if not problem_data:
            return jsonify({'error': 'No problem found'}), 404

        points = leaderboard_manager.process_points_for_submission(
            question_id=problem_data.id,
            question_title=problem_data.name,
            user_id=user_id,
            difficulty=difficulty
        )
    except Exception as e:
        return jsonify({'error': str(e)}), 400

    if not points:
        return jsonify({'error': 'No points given'}), 400
    return jsonify({'points': points}), 200

@bp.route('/problem/thread/<submission_thread_id>', methods=['GET'])
def get_problem_difficulty_thread_map(submission_thread_id: str) -> dict:
    print("submission_thread_id:", submission_thread_id)
    if not submission_thread_id:
        return jsonify({'error': 'thread id not provided'}), 400
    
    difficulty_thread_map = redis_client.get_decoded_dict(submission_thread_id)
    # Thread_id could be None or a map if the key exists
    return jsonify({'difficulty_thread_map': difficulty_thread_map}), 200


@bp.route('/problem/thread', methods=['POST'])
def cache_submission_thread_id():
    data = request.json
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    if not data.get('submission_channel_id') or not data.get('difficulty_thread_map') or not data.get('ttl'):
        return jsonify({'error': 'Submission channel ID or difficulty thread map not provided'}), 400
    
    
    submission_channel_id = data['submission_channel_id']
    difficulty_thread_map = data['difficulty_thread_map']
    ttl = data['ttl']

    redis_client.set_dict(submission_channel_id, difficulty_thread_map, ttl)
    return jsonify({'message': 'Thread ID cached'}), 200

@bp.route('/problem/thread/clear', methods=['POST'])
def clear_weekly_problem_redis_cache():
    redis_client.clear_cache()
    return jsonify({'message': 'Cache cleared'}), 200
