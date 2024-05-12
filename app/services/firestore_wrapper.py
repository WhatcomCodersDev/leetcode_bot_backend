from google.cloud import firestore
from datetime import datetime
from typing import Union, List
from constants import TITLE, TIMESTAMP, USER_ID, USER_SCORES, USERS_SOLVED, LEADERBOARD_COLLECTION, LEETCODE_COLLECTION, TEST_LEETCODE_COLLECTION, TEST_LEADERBOARD_COLLECTION
from google.cloud.firestore import CollectionReference, DocumentReference

class FirestoreWrapper:
    def __init__(self, project_name: str, environment: str = "development", database:str="github-commit-data"):
        self.db = firestore.Client(project=project_name, database=database)
        self.leetcode_collection = LEETCODE_COLLECTION if environment == "production" else TEST_LEETCODE_COLLECTION
        self.leaderboard_collection = LEADERBOARD_COLLECTION if environment == "production" else TEST_LEADERBOARD_COLLECTION


    def get_collection(self, collection_name: str) -> CollectionReference:
        try:
            collection_ref = self.db.collection(collection_name)
        except Exception as e:
            print(f"Failed to get collection with name {collection_name} because: {e}")
            raise
        return collection_ref
    
    def get_doc_ref(self, collection_ref: CollectionReference, document_name: str) -> DocumentReference:
        try:
            doc_ref = collection_ref.document(str(document_name))
        except Exception as e:
            print(f"Failed to get document with name {document_name} because: {e}")
            raise
        return doc_ref

    ## LEETCODE QUESTIONS MANAGER
    def update_question_document(self,
                                 question_id: str,
                                 question_title: str,
                                 last_asked_timestamp: datetime):

        collection_ref = self.get_collection(self.leetcode_collection)
        doc_ref = self.get_doc_ref(collection_ref, question_id)

        try:
            doc = doc_ref.get()
            if doc.exists:
                # Document exists, so we update it, specifically last_asked-timestamp

                doc_ref.update({TIMESTAMP: last_asked_timestamp})
                print(f"Updated question #{question_id} with new timestamp {last_asked_timestamp}.")
            else:
                # Document doesn't exist, so we create it with the initial user in users_solved
                question_data = {
                    TITLE: question_title,
                    TIMESTAMP: last_asked_timestamp,
                    USERS_SOLVED: []  # Initialize with no users
                }
                doc_ref.set(question_data)
                print(f"Question #{question_id} added successfully to the db")
                
        except Exception as e:
            print(f"Error in add_or_update_question for question #{question_id}: {e}")

    def add_or_update_question(self, 
                               question_id: str, 
                               question_title: str, 
                               last_asked_timestamp: datetime, 
                               user_id: str):
        collection_ref = self.get_collection(self.leetcode_collection)
        doc_ref = self.get_doc_ref(collection_ref, question_id)

        try:
            doc = doc_ref.get()
            if doc.exists:
                # Document exists, so we update it, specifically the users_solved list
                users_solved = doc.to_dict().get(USERS_SOLVED, [])
                if user_id not in users_solved:
                    users_solved.append(user_id)
                    doc_ref.update({USERS_SOLVED: users_solved, TIMESTAMP: last_asked_timestamp})
                print(f"Updated question #{question_id} with new user {user_id}.")
            else:
                #TODO - This might be deprecated now because in problem manager we create the question document
                # Document doesn't exist, so we create it with the initial user in users_solved
                question_data = {
                    TITLE: question_title,
                    TIMESTAMP: last_asked_timestamp,
                    USERS_SOLVED: [user_id]  # Initialize with the first user
                }
                doc_ref.set(question_data)
                print(f"Question #{question_id} added successfully to the db with initial user {user_id}.")
                
        except Exception as e:
            print(f"Error in add_or_update_question for question #{question_id}: {e}")
            raise e


    def add_question_asked(self, question_id: str, question_title:str, last_asked_timestamp: datetime, users_solved: List[str]=[]):
        question_data = {
            TITLE: question_title,
            TIMESTAMP: last_asked_timestamp,
            USERS_SOLVED: users_solved
        }
        try:
            collection_ref = self.get_collection(self.leetcode_collection)
            doc_ref = self.get_doc_ref(collection_ref, question_id)
            doc_ref.set(question_data)
            print(f"Question #{question_id} added successfuly to the db")
            
        except Exception as e:
            print(f"Problem adding question to db: {e}")

    def update_last_asked_timestamp(self, question_id: str, new_timestamp: datetime):
        collection_ref = self.get_collection(self.leetcode_collection)
        doc_ref = self.get_doc_ref(collection_ref, question_id)

        try:
            doc_ref.update({TIMESTAMP:new_timestamp})
            print(f"Last asked timestamp updated to {new_timestamp}")
        except Exception as e:
            print(f"Error updating last asked timestamp: {e}")

    def add_user_solved(self, question_id: str, user_id: str):
        collection_ref = self.get_collection(self.leetcode_collection)
        doc_ref = self.get_doc_ref(collection_ref, question_id)

        try:
            doc = doc_ref.get()
            if doc.exists:
                users_solved = doc.to_dict().get(USERS_SOLVED)
                users_solved.append(user_id)
                doc_ref.update({USERS_SOLVED: users_solved})

                print(f"Add {user_id} to list of users solved question #{question_id}")
            
        except Exception as e:
            print(f"Error updating list of user solving question #{question_id}: {e}")

    def check_if_question_was_asked(self, question_id: str):
        collection_ref = self.get_collection(self.leetcode_collection)
        doc_ref = self.get_doc_ref(collection_ref, question_id)
       
        try:
            doc = doc_ref.get()
            if doc.exists:
                return True
            else:
                return False
        except Exception as e:
            print(f'Error checking: {e}')

    ## LEADERBOARD MANAGER
    def validate_score(self, score: int):
        try: #make util function later
            int(score)
        except Exception as e:
            f"ERROR: Attempted to add non-int score for {score}" #If score is null, don't add/update the db
            raise 



    def add_or_update_user_score(self, user_id: str, score: int): #TODO make score an int
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
                total_scores = doc.to_dict().get(USER_SCORES)
                return total_scores
            else:
                return 0
        except Exception as e:
            print(f"Problem getting scores for user# {user_id}: {e}")

    def get_top_n_users_of_all_time(self, n: int = 5) -> List[dict]:
        collection_ref = self.get_collection(self.leaderboard_collection)
        leaderboard_top = (collection_ref
                           .order_by(USER_SCORES, direction=firestore.Query.DESCENDING)
                           .limit(n)
                           .stream())
        leaderboard_data = []
        for doc in leaderboard_top:
            data = doc.to_dict()
            print(data)
            leaderboard_data.append(data)

        return leaderboard_data






            
    