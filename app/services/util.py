from datetime import datetime

def handle_updating_submission_data(problem_id, data, review_data, problem_data):
    # Build submission data
    update_fields = {problem_id: {}}

    if 'user_rating' in data:
        update_fields[problem_id]['user_rating'] = data['user_rating']
    
    if 'last_reviewed_timestamp' in data:
        update_fields[problem_id]['last_reviewed_timestamp'] = datetime.now()

    if 'next_review_timestamp' in data:
        update_fields[problem_id]['next_review_timestamp'] = review_data['next_review_timestamp']
    
    
    update_fields[problem_id]['category'] = problem_data.category

    return update_fields