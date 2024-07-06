import pytz
from datetime import datetime, timezone, timedelta
from flask import Blueprint, request, jsonify
from app.services import leetcode_review_type_manager, fsrs_scheduler, submission_collection_manager

bp = Blueprint('crons', __name__, url_prefix='/tasks')

REVIEW_CATEGORY_KEY = 'review_types'

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

@bp.route('/review/daily', methods=['GET'])
def daily_task():
    '''
    1. Fetch all collections from users_problemtypes_for_review collection
    2. For each collection, iterate through each problem types
    3. For each problem in problem category, update the review_date
        if the review date has passed and the user has reviewed the problem then the review date should increase
        if the review date has passed and the user has not reviewed the problem then the review date should decrease
        there may exist a middle option. The spaced repetition algorithm should be used to determine the next review date
    4. Update the review date in the document
    
    5. If the user has reviewed all problem for that problem category, and the review dates are all
    above a week, then add a new problem category to the user's review types
    


    {uuid:
        dP: {problem 1, problem 2, problem 3}
        DFS: {problem 1, problem 2, problem 3}
    
    uuid2
        
    }

    Alternatively:
    
    Get and create some Metadata
    1. Fetch the problemtypes collection
    2. Load all problem data in a hashmap
        1. Keep a map of problem types to problems


    1. Iterate through each users leetcode submissions
        1. Filter and group the problems by problem category
        2. Iterate through each problem in the problem category
            1. Do the logic as before

            
    Actually, use submission manager to fetch the problems and filter by 'category' field

    '''

    all_user_uuids = submission_collection_manager.get_all_user_uuids() #Todo - This doesn't get all the uuids
    print("all_user_uuids:", all_user_uuids)
    for user_id in all_user_uuids:
        try:
            user_problems = submission_collection_manager.get_user_submissions(user_id)
            user_review_categories = leetcode_review_type_manager.get_problem_categories_marked_for_review_by_user(user_id)[REVIEW_CATEGORY_KEY]
            print("user_review_categories:", user_review_categories)
            user_problems_by_category = create_problem_category_to_problem_map(user_problems, user_review_categories)
            print("user_problems_by_category:", user_problems_by_category)
            for review_category, problems in user_problems_by_category.items():
                review_count = 0
                for problem in problems:
                    if 'next_review_timestamp' not in problem:
                        problem['next_review_timestamp'] = datetime.now()
                    try:
                        timewindow_in_memory = problem['next_review_timestamp'] + timedelta(days=1) # time window is 24 hours

                        ## Case 1: Successfully reviewed within the time window
                        ## last_reviewed: july 10 12pm
                        ## next_reviewed: july 10
                        ## time_window: july 11      

                        ## Conditions
                        ## 1. We are in the time window (between next_reviewed and time_window)
                        ## 2. The last_reviewed is within the time_window


                        ##      |-----------------|-----------------|

                        ##

                        if problem['next_review_timestamp'] and (datetime.now() >= make_naive(problem['next_review_timestamp']) and datetime.now() < make_naive(timewindow_in_memory)) \
                            and (problem['last_reviewed_timestamp'] >= problem['next_review_timestamp'] and problem['last_reviewed_timestamp'] < timewindow_in_memory):
                            print("Case 1: This user has successfully reviewed the problem within the time window")


                            REVIEWED_EASE = 4
                            ## TODO - Make its own function
                            if 'user_rating' in problem:
                                update_fields = {problem['problem_id']: {}}
                                review_data = fsrs_scheduler.schedule_review(problem, datetime.now(), ease=REVIEWED_EASE, interval=1, performance_rating=problem['user_rating'])
                                update_fields[problem['problem_id']]['next_review_timestamp'] = review_data['next_review_timestamp']
                                update_fields[problem['problem_id']]['last_reviewed_timestamp'] = problem['last_reviewed_timestamp']
                                update_fields[problem['problem_id']]['category'] = problem['category']

                                if 'user_rating' not in problem:
                                    update_fields[problem['problem_id']]['user_rating'] = 2
                                update_fields[problem['problem_id']]['user_rating'] = problem['user_rating']
                                submission_collection_manager.update_leetcode_submission(user_id, problem['problem_id'], update_fields)
                                review_count += 1



                        ## Case 2: Failed to review within the time window
                        ## last_reviewed: july 6
                        ## next_reviewed: july 10
                        ## time_window: july 11
                        print(datetime.now())
                        print(make_naive(problem['next_review_timestamp']))
                        if problem['next_review_timestamp'] and (datetime.now() >= make_naive(problem['next_review_timestamp']) and datetime.now() < make_naive(timewindow_in_memory)) \
                            and (problem['last_reviewed_timestamp'] < problem['next_review_timestamp'] and problem['last_reviewed_timestamp'] < timewindow_in_memory):
                            print("Case 2: This user has failed to review the problem within the time window")
                            ## It should still update the review date, but with a lower ease
                            FAILED_EASE = 2.5
                            update_fields = {problem['problem_id']: {}}
                            review_data = fsrs_scheduler.schedule_review(problem, datetime.now(), ease=FAILED_EASE, interval=1, performance_rating=2)
                            update_fields[problem['problem_id']]['next_review_timestamp'] = review_data['next_review_timestamp']
                            update_fields[problem['problem_id']]['last_reviewed_timestamp'] = problem['last_reviewed_timestamp']
                            update_fields[problem['problem_id']]['category'] = problem['category']

                            if 'user_rating' not in problem:
                                update_fields[problem['problem_id']]['user_rating'] = 2
                            update_fields[problem['problem_id']]['user_rating'] = problem['user_rating']
                            submission_collection_manager.update_leetcode_submission(user_id, problem['problem_id'], update_fields)


                        ## Case 3: Time window hasn't opened
                        if problem['next_review_timestamp'] and datetime.now() < make_naive(problem['next_review_timestamp']):
                            print("Case 3: Time window hasn't opened")
                            continue



                        # if problem['next_review_timestamp'] and datetime.now() > make_naive(problem['next_review_timestamp']):
                        #     update_fields = {problem['problem_id']: {}}
                        #     review_data = fsrs_scheduler.schedule_review(problem, datetime.now(), ease=2.5, interval=1, performance_rating=4)
                            
                            
                        #     update_fields[problem['problem_id']]['next_review_timestamp'] = review_data['next_review_timestamp']
                            
                        #     if 'last_reviewed_timestamp' in problem:
                        #         update_fields[problem['problem_id']]['last_reviewed_timestamp'] = problem['last_reviewed_timestamp']
                            
                        #     if 'category' in problem:
                        #         update_fields[problem['problem_id']]['category'] = problem['category']
                            
                        #     if 'user_rating' in problem:
                        #         update_fields[problem['problem_id']]['user_rating'] = problem['user_rating']

                        #     submission_collection_manager.update_leetcode_submission(user_id, problem['problem_id'], update_fields)
                        #     review_count += 1
                    except Exception as e:
                        print(f"Error in updating review for user {user_id} and problem {problem['problem_id']}: {e}")
                        continue
                    
                # If all problems have been reviewed, then add a new problem for that review category
                if review_count == len(problems):
                    # Recommend a problem using problem recommendation service
                    print("TODO - Add a new problem for that review category")

        except Exception as e:
            print(f"Error in updating reviews for user {user_id}: {e}")
            continue

    
    print("calling /review/daily endpoint")
    return "Updated all user's review successfully", 200

def create_problem_category_to_problem_map(user_problems, user_review_categories) -> dict:
    '''
    Create a map of problem categories to problems

    user_review_categories = {'Binary Search', 'DFS'}
    create map that is like {'Binary Search': [problem1, problem2], 'DFS': [problem1, problem2]}

    '''
    user_problems_by_category = {}
    for problem_generator in user_problems:
        problem = problem_generator.to_dict()
        problem_id = problem_generator.id
        # problem = problem.to_dict() # Gets {'1': {problem_data}}
        problem = next(iter(problem.values())) # Gets {problem_data}
        if 'category' in problem and problem['category'] in user_review_categories:
            if problem['category'] not in user_problems_by_category:
                user_problems_by_category[problem['category']] = []
            problem["problem_id"] = problem_id # Add the problem id to the problem for future
            user_problems_by_category[problem['category']].append(problem)
    
    return user_problems_by_category
