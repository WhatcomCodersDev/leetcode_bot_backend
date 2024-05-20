# leaderboard_manager.py
from app.services.databases.firestore.firestore_base import FirestoreBase
from google.cloud import firestore
from typing import List
from constants import USER_ID, USER_SCORES, LEADERBOARD_COLLECTION, TEST_LEADERBOARD_COLLECTION

'''
Handles interaction with leetcode_leaderboard collection

Collection: leetcode_leaderboard
Description: Stores users points
Document ID: User ID (uid)
Fields:
uid (string): Unique identifier for the user.
user_scores (int): The score for the ser
'''


class LeaderboardCollectionManager(FirestoreBase):
    def __init__(self, project_name: str, environment: str = "development", database: str = "github-commit-data"):
        super().__init__(project_name, environment, database)
        self.leaderboard_collection = LEADERBOARD_COLLECTION if environment == "production" else TEST_LEADERBOARD_COLLECTION

    def validate_score(self, score: int):
        try:
            int(score)
        except Exception as e:
            print(f"ERROR: Attempted to add non-int score for {score}")
            raise

    def add_or_update_user_score(self, user_id: str, score: int):
        self.validate_score(score)
        collection_ref = self.get_collection(self.leaderboard_collection)
        doc_ref = self.get_doc_ref(collection_ref, user_id)
        try:
            doc = doc_ref.get()
            if doc.exists:
                total_scores = doc.to_dict().get(USER_SCORES, 0)
                total_scores += score
                doc_ref.update({USER_SCORES: total_scores})
            else:
                user_data = {
                    USER_ID: user_id,
                    USER_SCORES: score
                }
                doc_ref.set(user_data)
        except Exception as e:
            print(f"Problem updating scores for user# {user_id}: {e}")
            raise e

    def get_user_score(self, user_id: str) -> int:
        collection_ref = self.get_collection(self.leaderboard_collection)
        doc_ref = self.get_doc_ref(collection_ref, user_id)
        try:
            doc = doc_ref.get()
            if doc.exists:
                return doc.to_dict().get(USER_SCORES, 0)
            else:
                return 0
        except Exception as e:
            print(f"Problem getting scores for user# {user_id}: {e}")

    def get_top_n_users_of_all_time(self, n: int = 5) -> List[dict]:
        collection_ref = self.get_collection(self.leaderboard_collection)
        leaderboard_top = collection_ref.order_by(USER_SCORES, direction=firestore.Query.DESCENDING).limit(n).stream()
        leaderboard_data = []
        for doc in leaderboard_top:
            data = doc.to_dict()
            print(data)
            leaderboard_data.append(data)
        return leaderboard_data

    # Add other methods for leaderboard management...
