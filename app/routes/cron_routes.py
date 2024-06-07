from flask import Blueprint, request, jsonify
from app.services import leaderboard_collection_manager

bp = Blueprint('crons', __name__, url_prefix='/tasks')

@bp.route('/review/daily', methods=['GET'])
def daily_task():
    print("calling /review/daily endpoint")
    # Your task logic here
    return 'Task executed successfully', 200