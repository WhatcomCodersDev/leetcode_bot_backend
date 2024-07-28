import os
from dotenv import load_dotenv

from app.services.problem_manager import ProblemManager
from app.services.user_problems_manager import UserProblemManager

from app.services.databases.firestore.leetcode_submissions import SubmissionCollectionManager
from app.services.databases.firestore.users import UserCollectionManager
from app.services.databases.firestore.leetcode_questions import LeetCodeCollectionManager
from app.services.databases.firestore.leetcode_reviewTypes import UsersLeetcodeReviewCategoriesCollectionManager

from app.services.databases.redis.redis_client import RedisClient
from app.services.space_repetition.scheduler import FSRSScheduler
from app.services.space_repetition.similarity_score_adapter import SimilarityScoreAdapter
from app.services.space_repetition.problem_ranker import ProblemRanker

load_dotenv()


environment = os.getenv("ENVIRONMENT", "development")  # Default to development if not set
gc_project_name = os.getenv("PROJECT_NAME")

redis_host = os.getenv("REDIS_HOST")
redis_port = int(os.getenv("REDIS_PORT"))
redis_password = os.getenv("REDIS_PWD")


redis_client = RedisClient(redis_host, redis_port, redis_password) #TODO: pass in the redis host, port, and password based on configs

# Firestore Collection Managers
submission_collection_manager = SubmissionCollectionManager(gc_project_name, environment)
user_collection_manager = UserCollectionManager(gc_project_name, environment)
leetcode_collection_manager = LeetCodeCollectionManager(gc_project_name, environment)
leetcode_review_type_manager = UsersLeetcodeReviewCategoriesCollectionManager(gc_project_name, environment)

# Services - TODO - rename
problem_manager = ProblemManager(leetcode_collection_manager, redis_client)
user_problem_manager = UserProblemManager(submission_collection_manager, problem_manager)

fsrs_scheduler = FSRSScheduler()
# similarity_score_adapter = SimilarityScoreAdapter()
# problem_ranker = ProblemRanker()
