# Routes that handle fetching problems
'''
1. Get a problem at random from spreadsheet based on difficulty
2. Get a problem based on id
3. Get a problem based on difficulty
4. Get a problem based on tag

'''
from flask import Blueprint, request, jsonify
from app.services import problem_manager

bp = Blueprint('problems', __name__, url_prefix='/problems')

@bp.route('/all', methods=['GET'])
def get_all_problems():
    problems = problem_manager.get_all_problems()
    return jsonify(problems), 200

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

# Used by Leetcode bot to get a random problem as per user request
@bp.route('/<problem_difficulty>/request', methods=['GET'])
def get_problem_user_request(problem_difficulty):
    if not problem_difficulty:
        return jsonify({'error': 'Problem difficulty not provided'}), 400

    # TODO: use discord_id for something
    discord_id = request.args.get('discord_id')
    if not discord_id:
        return jsonify({'error': 'User ID not provided'}), 400

    if problem_difficulty not in ['easy', 'medium', 'hard']:
        return jsonify({'error': 'Invalid difficulty'}), 400

    # select_problem_at_random() = no cache
    problem = problem_manager.select_problem_at_random(problem_difficulty)
    if not problem:
        return jsonify({'error': 'No problem found'}), 404
    
    return jsonify(problem), 200