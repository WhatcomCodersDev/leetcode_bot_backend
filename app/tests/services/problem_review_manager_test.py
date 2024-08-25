import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta
from app.services.user_submissions_reviewing.problem_to_review_data import ProblemToReview
from app.services.space_repetition.scheduler import FSRSScheduler
from app.services.user_submissions_reviewing.problem_review_manager import ProblemReviewManager
from app.databases.firestore.leetcode_submissions import FirestoreSubmissionCollectionWrapper
from app.databases.firestore.leetcode_reviewTypes import FirestoreUsersLeetcodeReviewCategoriesCollectionWrapper
from app.services.time_utils import make_aware, make_naive

@pytest.fixture
def firestore_submission_collection_wrapper():
    return MagicMock(spec=FirestoreSubmissionCollectionWrapper)

@pytest.fixture
def firestore_leetcode_review_type_wrapper():
    return MagicMock(spec=FirestoreUsersLeetcodeReviewCategoriesCollectionWrapper)

@pytest.fixture
def fsrs_scheduler():
    return FSRSScheduler()

@pytest.fixture
def problem_review_manager(firestore_submission_collection_wrapper, firestore_leetcode_review_type_wrapper, fsrs_scheduler):
    return ProblemReviewManager(
        firestore_submission_collection_wrapper,
        firestore_leetcode_review_type_wrapper,
        fsrs_scheduler
    )

def test_initialization(problem_review_manager, firestore_submission_collection_wrapper, firestore_leetcode_review_type_wrapper, fsrs_scheduler):
    assert problem_review_manager.firestore_submission_collection_wrapper == firestore_submission_collection_wrapper
    assert problem_review_manager.firestore_leetcode_review_type_wrapper == firestore_leetcode_review_type_wrapper
    assert problem_review_manager.fsrs_scheduler == fsrs_scheduler

# @patch('app.databases.firestore.leetcode_submissions.FirestoreSubmissionCollectionWrapper.get_user_submissions')
# @patch('app.databases.firestore.leetcode_reviewTypes.FirestoreUsersLeetcodeReviewCategoriesCollectionWrapper.get_problem_categories_marked_for_review_by_user')
# @patch('app.services.problem_sheet.problem_manager.ProblemManager.get_problem_by_id')
# def test_get_user_problems_by_category(mock_get_problem_by_id, 
#                                        mock_get_problem_categories_marked_for_review_by_user, 
#                                        mock_get_user_submissions, 
#                                        problem_review_manager):
#     # Mocking Firestore document snapshots for user submissions
#     mock_doc_1 = MagicMock()
#     mock_doc_1.id = '1'
#     mock_doc_1.to_dict.return_value = {'category': 'Arrays'}
    
#     mock_doc_2 = MagicMock()
#     mock_doc_2.id = '2'
#     mock_doc_2.to_dict.return_value = {'category': 'Strings'}

#     mock_get_user_submissions.return_value = [mock_doc_1, mock_doc_2]

#     # Mocking the categories marked for review by the user
#     mock_get_problem_categories_marked_for_review_by_user.return_value = {'review_types': ['Arrays']}

#     # Mocking the method to get problem by ID
#     mock_get_problem_by_id.side_effect = lambda problem_id: {
#         'id': problem_id, 
#         'name': f'Problem {problem_id}', 
#         'category': 'Arrays' if problem_id == '1' else 'Strings'
#     }

#     # Run the method being tested
#     result = problem_review_manager.get_user_problems_by_category('test-user-id')

#     # Define the expected result
#     expected_result = {
#         'Arrays': [ProblemToReview(problem_id='1', category='Arrays')],
#     }

#     # Validate the result
#     assert result == expected_result

def test_create_problem_category_to_problem_map(problem_review_manager):
    # Mocking the user problems (DocumentSnapshot objects)
    mock_doc_1 = MagicMock()
    mock_doc_1.id = '127'
    mock_doc_1.to_dict.return_value = {
        '127': {
            'last_reviewed_timestamp': datetime(2024, 7, 30, 5, 47, 0, 762358),
            'user_rating': 3,
            'next_review_timestamp': None,
            'streak': 0,
            'category': 'Binary Search'
        }
    }
    
    mock_doc_2 = MagicMock()
    mock_doc_2.id = '128'
    mock_doc_2.to_dict.return_value = {
        '128': {
            'last_reviewed_timestamp': datetime(2024, 7, 31, 5, 47, 0, 762358),
            'user_rating': 4,
            'next_review_timestamp': None,
            'streak': 1,
            'category': 'DFS'
        }
    }
    
    mock_doc_3 = MagicMock()
    mock_doc_3.id = '129'
    mock_doc_3.to_dict.return_value = {
        '129': {
            'last_reviewed_timestamp': datetime(2024, 8, 1, 5, 47, 0, 762358),
            'user_rating': 2,
            'next_review_timestamp': None,
            'streak': 0,
            'category': 'Binary Search'
        }
    }
    
    user_problems = [mock_doc_1, mock_doc_2, mock_doc_3]

    # Mocking user review categories
    user_review_categories = {'Binary Search': 'reviewed', 'DFS': 'reviewed'}

    # Call the method under test
    result = problem_review_manager.create_problem_category_to_problem_map(
        user_problems=user_problems, 
        user_review_categories=user_review_categories
    )

    # Define the expected result
    expected_result = {
        'Binary Search': [
            ProblemToReview(
                problem_id='127', 
                last_reviewed_timestamp=datetime(2024, 7, 30, 5, 47, 0, 762358),
                user_rating=3,
                next_review_timestamp=None,
                streak=0,
                category='Binary Search'
            ),
            ProblemToReview(
                problem_id='129', 
                last_reviewed_timestamp=datetime(2024, 8, 1, 5, 47, 0, 762358),
                user_rating=2,
                next_review_timestamp=None,
                streak=0,
                category='Binary Search'
            )
        ],
        'DFS': [
            ProblemToReview(
                problem_id='128', 
                last_reviewed_timestamp=datetime(2024, 7, 31, 5, 47, 0, 762358),
                user_rating=4,
                next_review_timestamp=None,
                streak=1,
                category='DFS'
            )
        ]
    }

    # Validate the result
    assert result == expected_result


def test_user_reviewed_problem_within_timewindow(problem_review_manager):
    '''Case 2: This user has successfully reviewed the problem within the time window
        


        Conditions
        1. The current time is within the time window (between next_reviewed and time_window)
        2. The last_reviewed is within the time_window

        Current Time: july 10 - july 11  


            |-----------------|-----------------|
        next_reviewed    last_reviewed    time_window
    '''
    problem_to_review = MagicMock(spec=ProblemToReview)
    
    # Setting up timestamps
    next_review_timestamp = datetime.now() - timedelta(hours=10)  # 10 hours ago
    last_reviewed_timestamp = datetime.now() - timedelta(hours=5)  # 5 hour ago
    timewindow_in_memory = datetime.now() - timedelta(hours=10) + timedelta(days=1)  # 1 day from the next_review_timestamp
    
    # Mocking return values
    problem_to_review.get_next_review_timestamp.return_value = next_review_timestamp
    problem_to_review.get_last_reviewed_timestamp.return_value = last_reviewed_timestamp

    result = problem_review_manager.user_reviewed_problem_within_timewindow(problem_to_review, timewindow_in_memory)

    # Assert the result is True for Case 1 logic
    assert result is True

def test_user_failed_to_review_problem_within_timewindow(problem_review_manager):
    '''Case 4: This user has failed to review the problem within the time window
    
        Conditions
        1. We were in the time window and it has finished (current time is after next_reviewed and time_window)
        2. The last_reviewed is not within the time_window
                
            
        Current Time: july 11 (after time window)

            |-----------------|-----------------|----------------------------|
            last_reviewed    next_reviewed    time_window/current_time      now (failed to review)
    '''
    problem_to_review = MagicMock(spec=ProblemToReview)
    
    # Setting up timestamps
    next_review_timestamp = datetime.now() - timedelta(hours=10)  # 10 hours ago
    last_reviewed_timestamp = datetime.now() - timedelta(hours=11)  # 11 hour ago
    timewindow_in_memory = datetime.now() - timedelta(hours=9)  # Lets say the time window was 9 hours ago
    

    problem_to_review.get_next_review_timestamp.return_value = next_review_timestamp
    problem_to_review.get_last_reviewed_timestamp.return_value = last_reviewed_timestamp

    result = problem_review_manager.user_failed_to_review_problem_within_timewindow(problem_to_review, timewindow_in_memory)

    # The user reviewed the problem outside the time window, before next_review and after time_window
    assert result is True

def test_user_has_not_reviewed_but_time_window_is_still_open(problem_review_manager):
    '''Case 3: The review window has opened, but the user has not reviewed the problem yet, but the time window is still open
                
            
        Current Time: july 11 (after time window)

            |-----------------|-----------------|
            last_reviewed    next_reviewed    time_window/current_time
    '''
    problem_to_review = MagicMock(spec=ProblemToReview)
    
    problem_to_review = MagicMock(spec=ProblemToReview)
    
    # Setting up timestamps
    next_review_timestamp = datetime.now() - timedelta(hours=10)  # 10 hours ago
    last_reviewed_timestamp = datetime.now() - timedelta(hours=11)  # 11 hour ago
    timewindow_in_memory = datetime.now() - timedelta(hours=10) + timedelta(days=1)  # 1 day from the next_review_timestamp
    # The user still has time to review the problem, so they haven't failed

    problem_to_review.get_next_review_timestamp.return_value = next_review_timestamp
    problem_to_review.get_last_reviewed_timestamp.return_value = last_reviewed_timestamp


    result = problem_review_manager.user_has_not_reviewed_but_time_window_is_still_open(problem_to_review, timewindow_in_memory)

    assert result is True

def test_timewindow_not_open_yet(problem_review_manager):
    '''
    Case 1: Time window hasn't opened
        
    Conditions
    1. The current time is before the next_reviewed


        |---------------------|------------------|------------------|
        last_reviewed      current_time       next_reviewed       time_window
    
    '''
    problem_to_review = MagicMock(spec=ProblemToReview)
    next_review_timestamp = datetime.now() + timedelta(hours=10)  # 10 hours in the future
    problem_to_review.get_next_review_timestamp.return_value = next_review_timestamp

    result = problem_review_manager.timewindow_not_open_yet(problem_to_review)

    assert result is True
