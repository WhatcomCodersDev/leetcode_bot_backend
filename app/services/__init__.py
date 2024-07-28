import os
from dotenv import load_dotenv

from app.services.problem_sheet.problem_manager import ProblemManager
from app.services.user_submissions_reviewing.user_problems_manager import UserProblemManager
from app.services.user_submissions_reviewing.problem_review_manager import ProblemReviewManager

from app.databases.firestore.leetcode_submissions import FirestoreSubmissionCollectionWrapper
from app.databases.firestore.users import FirestoreUserCollectionWrapper
from app.databases.firestore.leetcode_questions import FirestoreLeetCodeCollectionWrapper
from app.databases.firestore.leetcode_reviewTypes import FirestoreUsersLeetcodeReviewCategoriesCollectionWrapper

from app.services.space_repetition.scheduler import FSRSScheduler
from app.services.space_repetition.similarity_score_adapter import SimilarityScoreAdapter
from app.services.space_repetition.problem_ranker import ProblemRanker

load_dotenv()


environment = os.getenv("ENVIRONMENT", "development")  # Default to development if not set
gc_project_name = os.getenv("PROJECT_NAME")


# Firestore Collection Managers
firestore_submission_collection_wrapper = FirestoreSubmissionCollectionWrapper(gc_project_name, environment)
firestore_user_collection_wrapper = FirestoreUserCollectionWrapper(gc_project_name, environment)
firestore_leetcode_collection_wrapper = FirestoreLeetCodeCollectionWrapper(gc_project_name, environment)
firestore_leetcode_review_type_wrapper = FirestoreUsersLeetcodeReviewCategoriesCollectionWrapper(gc_project_name, environment)

# Services - TODO - rename
problem_manager = ProblemManager(firestore_leetcode_collection_wrapper)
user_problem_manager = UserProblemManager(firestore_submission_collection_wrapper, problem_manager)
fsrs_scheduler = FSRSScheduler()
problem_review_manager = ProblemReviewManager(firestore_submission_collection_wrapper, firestore_leetcode_review_type_wrapper, fsrs_scheduler)

# similarity_score_adapter = SimilarityScoreAdapter()
# problem_ranker = ProblemRanker()
