import os
from dotenv import load_dotenv

from app.services.problem_manager import ProblemManager
from app.services.firestore_wrapper import FirestoreWrapper
from app.services.leaderboard_manager import LeaderboardManager
from app.services.redis_client import RedisClient

load_dotenv()


# Todo - Load environment variables somewhere else
environment = os.getenv("ENVIRONMENT", "development")  # Default to development if not set
gc_project_name = os.getenv("PROJECT_NAME")

redis_host = os.getenv("REDIS_HOST")
redis_port = int(os.getenv("REDIS_PORT"))
redis_password = os.getenv("REDIS_PWD")


firestore_wrapper = FirestoreWrapper(gc_project_name, environment) #TODO: pass in the firestore project name and environment based on configs
redis_client = RedisClient(redis_host, redis_port, redis_password) #TODO: pass in the redis host, port, and password based on configs

problem_manager = ProblemManager(firestore_wrapper, redis_client)
leaderboard_manager = LeaderboardManager(firestore_wrapper, redis_client)