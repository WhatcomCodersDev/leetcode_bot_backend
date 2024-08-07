import pytz
from datetime import datetime, timezone, timedelta
from app.services.problem_sheet.problem import Problem
from typing import Dict 

def handle_updating_submission_data(
        problem_id: str, 
        submission_data: Dict[str, str], 
        review_data: Dict[str, str],
        problem_data: Problem,
        ):
    # Build submission data
    update_fields = {problem_id: {}}

    if 'user_rating' in submission_data:
        update_fields[problem_id]['user_rating'] = submission_data['user_rating']
    
    if 'last_reviewed_timestamp' in submission_data:
        update_fields[problem_id]['last_reviewed_timestamp'] = convert_dateime_now_to_pt()

    
    if review_data and 'next_review_timestamp' in submission_data:
        update_fields[problem_id]['next_review_timestamp'] = review_data['next_review_timestamp']
    elif 'next_review_timestamp' in submission_data:
        update_fields[problem_id]['next_review_timestamp'] = submission_data['next_review_timestamp']
    
    update_fields[problem_id]['category'] = problem_data.get_category()

    return update_fields


PT = pytz.timezone('US/Pacific')


def make_aware(naive_dt):
    """Make a naive datetime aware in PT time zone."""
    # Localize the naive datetime to PT
    aware_dt = PT.localize(naive_dt)
    return aware_dt

def make_naive(aware_dt):
    pt_dt = aware_dt.astimezone(PT)
    naive_dt = pt_dt.replace(tzinfo=None)
    return naive_dt

def convert_dateime_now_to_pt():
    """Convert the current UTC time to PT time zone."""
    # Get the current UTC time
    utc_now = datetime.now(timezone.utc)
    # Convert the UTC time to PT time zone
    pt_now = utc_now.astimezone(PT)
    return pt_now