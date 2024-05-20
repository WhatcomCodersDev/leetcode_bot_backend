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

