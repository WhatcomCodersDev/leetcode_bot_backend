# Routes that handle getting/setting data for leaderboard
'''
1. Get user score
2. Get top n users
3. Add or update user score

'''

from flask import Blueprint, request, jsonify
from app.services import leaderboard_manager, firestore_wrapper

bp = Blueprint('leaderboard', __name__, url_prefix='/leaderboard')

@bp.route('/', methods=['GET'])
def get_leaderboard():
    try:
        leaderboard_data = firestore_wrapper.get_top_n_users_of_all_time(n=5)
    except Exception as e:
        return jsonify({'error': f"Problem getting leaderboard data: {e}"}), 500    

    if not leaderboard_data:
        return jsonify({'error': 'No data found'}), 404
  
    return jsonify({'leaderboard_data': leaderboard_data}), 200
