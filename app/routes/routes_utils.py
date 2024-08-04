from app.services import  problem_manager


def validate_request_data(problem_id, data):
    """Validates the incoming request data.
    
    Args:
        problem_id (str): problem ID
        data (dict): request JSON data
    
    Returns:
        tuple: (bool, str) indicating success and error message if any
    """
    if not data:
        return False, 'No data provided'
    
    if not problem_id:
        return False, 'Problem ID not provided'
    
    if not data.get('discord_id') and not data.get('user_id'):
        return False, 'Discord ID or User ID not provided'
    
    return True
