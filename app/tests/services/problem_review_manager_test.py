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

@patch('app.databases.firestore.leetcode_submissions.FirestoreSubmissionCollectionWrapper.get_user_submissions')
@patch('app.databases.firestore.leetcode_reviewTypes.FirestoreUsersLeetcodeReviewCategoriesCollectionWrapper.get_problem_categories_marked_for_review_by_user')
@patch('app.services.problem_sheet.problem_manager.ProblemManager.get_problem_by_id')
def test_get_user_problems_by_category(mock_get_problem_by_id, mock_get_problem_categories_marked_for_review_by_user, mock_get_user_submissions, problem_review_manager):
    mock_get_user_submissions.return_value = [
        MagicMock(id='1', to_dict=MagicMock(return_value={'1': {'category': 'Arrays'}})),
        MagicMock(id='2', to_dict=MagicMock(return_value={'2': {'category': 'Strings'}})),
    ]
    mock_get_problem_categories_marked_for_review_by_user.return_value = {'review_types': ['Arrays']}
    mock_get_problem_by_id.side_effect = lambda problem_id: {'id': problem_id, 'name': f'Problem {problem_id}', 'category': 'Arrays' if problem_id == '1' else 'Strings'}

    result = problem_review_manager.get_user_problems_by_category('test-user-id')
    expected_result = {
        'Arrays': [ProblemToReview(problem_id='1', category='Arrays')],
    }

    assert result == expected_result

@patch('app.databases.firestore.leetcode_submissions.FirestoreSubmissionCollectionWrapper.update_leetcode_submission')
def test_update_review_date(mock_update_leetcode_submission, problem_review_manager):
    problem_to_review = ProblemToReview(
        problem_id='1',
        category='Arrays',
        user_rating=4,
        last_reviewed_timestamp=datetime(2023, 1, 1),
        next_review_timestamp=datetime(2023, 1, 2),
        streak=0
    )

    review_data = {
        'next_review_timestamp': datetime(2023, 1, 3)
    }

    problem_review_manager.update_review_date('test-user-id', problem_to_review, review_data)

    mock_update_leetcode_submission.assert_called_once_with(
        'test-user-id',
        '1',
        {
            'problem_id': '1',
            'category': 'Arrays',
            'user_rating': 4,
            'last_reviewed_timestamp': datetime(2023, 1, 1),
            'next_review_timestamp': datetime(2023, 1, 3),
            'streak': 0
        }
    )

@patch('app.services.problem_review_manager.ProblemReviewManager.update_review_date')
@patch('app.services.problem_review_manager.ProblemReviewManager.case1_logic')
@patch('app.services.problem_review_manager.ProblemReviewManager.case2_logic')
@patch('app.services.problem_review_manager.ProblemReviewManager.case3_logic')
def test_handle_review_logic(mock_case3_logic, mock_case2_logic, mock_case1_logic, mock_update_review_date, problem_review_manager):
    problem_to_review = ProblemToReview(
        problem_id='1',
        category='Arrays',
        user_rating=4,
        last_reviewed_timestamp=datetime(2023, 1, 1),
        next_review_timestamp=datetime(2023, 1, 2),
        streak=0
    )
    user_id = 'test-user-id'
    timewindow_in_memory = datetime(2023, 1, 3)

    # Case 1 Logic
    mock_case1_logic.return_value = True
    review_count = problem_review_manager.handle_review_logic(user_id, problem_to_review, timewindow_in_memory)
    assert review_count == 1
    mock_update_review_date.assert_called()

    # Case 2 Logic
    mock_case1_logic.return_value = False
    mock_case2_logic.return_value = True
    review_count = problem_review_manager.handle_review_logic(user_id, problem_to_review, timewindow_in_memory)
    assert review_count == 0
    mock_update_review_date.assert_called()

    # Case 3 Logic
    mock_case2_logic.return_value = False
    mock_case3_logic.return_value = True
    review_count = problem_review_manager.handle_review_logic(user_id, problem_to_review, timewindow_in_memory)
    assert review_count == 0

def test_case1_logic(problem_review_manager):
    problem_to_review = ProblemToReview(
        problem_id='1',
        category='Arrays',
        user_rating=4,
        last_reviewed_timestamp=make_aware(datetime(2023, 1, 10, 12, 0)),
        next_review_timestamp=make_aware(datetime(2023, 1, 10, 10, 0)),
        streak=0
    )
    timewindow_in_memory = make_aware(datetime(2023, 1, 11))

    result = problem_review_manager.case1_logic(problem_to_review, timewindow_in_memory)
    assert result

def test_case2_logic(problem_review_manager):
    problem_to_review = ProblemToReview(
        problem_id='1',
        category='Arrays',
        user_rating=4,
        last_reviewed_timestamp=make_aware(datetime(2023, 1, 6)),
        next_review_timestamp=make_aware(datetime(2023, 1, 10)),
        streak=0
    )
    timewindow_in_memory = make_aware(datetime(2023, 1, 11))

    result = problem_review_manager.case2_logic(problem_to_review, timewindow_in_memory)
    assert result

def test_case3_logic(problem_review_manager):
    problem_to_review = ProblemToReview(
        problem_id='1',
        category='Arrays',
        user_rating=4,
        last_reviewed_timestamp=make_aware(datetime(2023, 1, 6)),
        next_review_timestamp=make_aware(datetime(2023, 1, 10)),
        streak=0
    )

    result = problem_review_manager.case3_logic(problem_to_review)
    assert result
