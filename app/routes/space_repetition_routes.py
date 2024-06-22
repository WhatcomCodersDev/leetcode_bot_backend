# Routes that handle space repetition
'''


'''
from datetime import datetime
from flask import Blueprint, request, jsonify
from app.services import fsrs_scheduler, submission_manager, user_manager, problem_manager

bp = Blueprint('space_repetition', __name__, url_prefix='/space_repetition')


@bp.route('/<problem_id>/submit', methods=['POST'])
def handle_problem_submission(problem_id):
    data = request.json
    print(data)
    if not data:
        print('No data provided')
        return jsonify({'error': 'No data provided'}), 400
    
    if not problem_id:
        return jsonify({'error': 'Problem ID not provided'}), 400
    
    problem_data = problem_manager.get_problem_by_id(int(problem_id))
    if 'user_rating' not in data:
        user_rating = 3 #default
        

    if not data.get('discord_id') and not data.get('user_id'):
        return jsonify({'error': 'Discord ID or User ID not provided'}), 400
    
   
    if not data.get('solved') and not data.get('attempted'):
        print('Attempted or solved not provided')
        return jsonify({'error': 'Attempted or solved not provided'}), 400

    if not problem_id:
        print('ID not provided')
        return jsonify({'error': 'ID not provided'}), 400
    
    if 'attempted' not in data and 'solved' not in data:
        return jsonify({'error': 'Attempted or Solved not provided'}), 400

    try:
        # Get user UUID
        if data.get('discord_id'):
            user_uuid = user_manager.get_uuid_from_discord_id(data['discord_id'])
        else:
            user_uuid = data['user_id']

        # First determine next time to review
        review_data = fsrs_scheduler.schedule_review(problem_id, 
                                                     datetime.now(), 
                                                     ease=2.5, 
                                                     interval=1, 
                                                     performance_rating=4) #todo pass user rating instead
        
        # Build submission data
        update_fields = {problem_id: {}}
        update_fields[problem_id]['user_rating'] = user_rating
        
        if data.get('solved'):
            update_fields[problem_id]['solved_timestamp'] = datetime.now()
            update_fields[problem_id]['last_reviewed_timestamp'] = datetime.now()

        
        if data.get('attempted'):
            update_fields[problem_id]['attempted_timestamp'] = datetime.now()
            update_fields[problem_id]['last_reviewed_timestamp'] = datetime.now()

        update_fields[problem_id]['next_review_timestamp'] = review_data['next_review_timestamp']
        update_fields[problem_id]['category'] = problem_data.category
        
        # Update datastore
        submission_manager.update_leetcode_submission(user_uuid,
                                                      problem_id, 
                                                      update_fields)
    
    except ValueError:
        print('Invalid ID')
        return jsonify({'error': 'Invalid ID'}), 400

    if not review_data:
        print('No problem found')
        return jsonify({'error': 'No problem found'}), 404
    
    return jsonify(review_data), 200

@bp.route('/daily_reminder', methods=['GET'])
def handle_daily_reminder():
    uuid_to_problems_id = submission_manager.get_problem_past_reviewed_date()

    discord_id_to_problems = {}
    for uuid, problems_id in uuid_to_problems_id.items():
        print(uuid, problems_id)

        if len(problems_id) == 0:
            continue

        discord_id = user_manager.get_discord_id_from_uuid(uuid)
        print(discord_id)
        discord_id_to_problems[discord_id] = []

        for prob_id in problems_id:
            prob_data = problem_manager.get_problem_by_id(int(prob_id))
            discord_id_to_problems[discord_id].append(prob_data)
    
    print(discord_id_to_problems)
    return jsonify({'discord_id_to_problems': discord_id_to_problems}), 200