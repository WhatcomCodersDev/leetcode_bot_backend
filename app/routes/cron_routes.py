from flask import Blueprint
from app.services import problem_review_manager
from app.services.time_utils import make_aware, make_naive

bp = Blueprint('crons', __name__, url_prefix='/tasks')


@bp.route('/review/daily', methods=['GET'])
def daily_task():

    all_user_uuids = problem_review_manager.__get_all_user_uuids__()
    print("all_user_uuids:", all_user_uuids)
    for user_id in all_user_uuids:
        try:
            problem_review_manager.process_user_reviews(user_id)
        except Exception as e:
            print(f"Error in updating reviews for user {user_id}: {e}")
    return "Updated all user's review successfully", 200
