# leetcode_manager.py
import uuid
from app.services.databases.firestore.firestore_base import FirestoreBase
from datetime import datetime
from typing import Dict, Union
from constants import USER_SUBMISSION_COLLECTION

'''
Handles interaction with users_leetcode_submission collection

Collection: users_leetcode_submission

Description: Stores data related to users submission to leetcode questions
Document ID: user_id (uuid)
Subcollections:
    problems
        Description:
        Document ID: problem_id (int)
        Fields:
            - difficulty (int): A difficulty scale from 0-5 on how hard the problem was for them
            - last_attempt_timestamp (date): Timestamp of the last time they’ve attempted the problem
            - last_solved_timestamp (date): Timestamp of the last time they've solved the problem
            - next_review_timestamp (date): Timestamp of the next time they should review the problem

'''

class SubmissionCollectionManager(FirestoreBase):
    def __init__(self, project_name: str, environment: str = "development", database: str = "github-commit-data"):
        super().__init__(project_name, environment, database)
        self.uuid_collection = USER_SUBMISSION_COLLECTION if environment == "production" else USER_SUBMISSION_COLLECTION

    def update_leetcode_submission(self, 
                                   uuid: str,
                                   problem_id: str, 
                                   update_fields: Dict[int, Union[int, datetime]],
                                   ):
        '''
        1. Get the user's submission document by uuid
        2. If user's submission document doesn't exist, create it with the initial submission
        3. Else, update the submission with the new submission data

        Note: Submission could be an attempt or solving the problem. We always assume
        at least one is not None, so we can update the submission

        This means that one timestamp will remain the same, while the other will be updated
        '''
                                  
        collection_ref = self.get_collection(self.uuid_collection)
        doc_ref = self.get_doc_ref(collection_ref, uuid)
        try:
            # Get the user's submission document
            doc = doc_ref.get()
            subcollection_ref = doc_ref.collection('problems')
            subcollection_doc_ref = subcollection_ref.document(str(problem_id))
        except Exception as e:
            print(f"Error in update_leetcode_submission for user {uuid}: {e}")
            raise e
        



        try:
            subcollection_doc = subcollection_doc_ref.get()

            if subcollection_doc.exists:
                # Document exists, so we update it, specifically last_asked-timestamp
                subcollection_doc_ref.update(update_fields)
                print(f"Updated submission for problem #{problem_id} for user {uuid}.")
            else:
                # Document doesn't exist, so we create it with the initial user in users_solved
               
                subcollection_doc_ref.set(update_fields) #todo - make problems a constant
                print(f"Submission for problem #{problem_id} added successfully to the db for user {uuid}")
                
        except Exception as e:
            print(f"Error in update_leetcode_submission for user {uuid}: {e}")
            raise e
        


