# leetcode_manager.py
from app.databases.firestore.firestore_base import FirestoreBase
from datetime import datetime
from typing import List
from constants import TITLE, TIMESTAMP, USERS_SOLVED, LEETCODE_COLLECTION, TEST_LEETCODE_COLLECTION

'''
Handles interaction with leetcode_questions collection

Collection: leetcode_questions
Description: Stores data related to leetcode questions
Document ID: Leetcode question Id (int)
Fields:
    - last_timestamp (date): timestamp of the last time the leetcode question was asked in a weekly challenge
    - title (string): Title of the leetcode question
    - user_solved (list): List of discord ids of users who have solved the leetcode question from the weekly challenge

'''

class FirestoreLeetCodeCollectionWrapper(FirestoreBase):
    def __init__(self, project_name: str, environment: str = "development", database: str = "github-commit-data"):
        super().__init__(project_name, environment, database)
        self.leetcode_collection = LEETCODE_COLLECTION if environment == "production" else TEST_LEETCODE_COLLECTION

    def update_question_document(self, question_id: str, question_title: str, last_asked_timestamp: datetime):
        collection_ref = self.get_collection(self.leetcode_collection)
        doc_ref = self.get_doc_ref(collection_ref, question_id)
        try:
            doc = doc_ref.get()
            if doc.exists:
                doc_ref.update({TIMESTAMP: last_asked_timestamp})
                print(f"Updated question #{question_id} with new timestamp {last_asked_timestamp}.")
            else:
                question_data = {
                    TITLE: question_title,
                    TIMESTAMP: last_asked_timestamp,
                    USERS_SOLVED: []
                }
                doc_ref.set(question_data)
                print(f"Question #{question_id} added successfully to the db")
        except Exception as e:
            print(f"Error in update_question_document for question #{question_id}: {e}")

    def add_or_update_question(self, question_id: str, question_title: str, last_asked_timestamp: datetime, user_id: str):
        collection_ref = self.get_collection(self.leetcode_collection)
        doc_ref = self.get_doc_ref(collection_ref, question_id)
        try:
            doc = doc_ref.get()
            if doc.exists:
                users_solved = doc.to_dict().get(USERS_SOLVED, [])
                if user_id not in users_solved:
                    users_solved.append(user_id)
                    doc_ref.update({USERS_SOLVED: users_solved, TIMESTAMP: last_asked_timestamp})
                print(f"Updated question #{question_id} with new user {user_id}.")
            else:
                question_data = {
                    TITLE: question_title,
                    TIMESTAMP: last_asked_timestamp,
                    USERS_SOLVED: [user_id]
                }
                doc_ref.set(question_data)
                print(f"Question #{question_id} added successfully to the db with initial user {user_id}.")
        except Exception as e:
            print(f"Error in add_or_update_question for question #{question_id}: {e}")
            raise e

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