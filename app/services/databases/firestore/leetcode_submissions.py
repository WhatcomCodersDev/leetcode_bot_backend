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
            - user_rating (int): A difficulty scale from 0-5 on how hard the problem was for them
            - last_attempt_timestamp (date): Timestamp of the last time they’ve attempted the problem
            - last_solved_timestamp (date): Timestamp of the last time they've solved the problem
            - next_review_timestamp (date): Timestamp of the next time they should review the problem

'''

class SubmissionCollectionManager(FirestoreBase):
    def __init__(self, project_name: str, environment: str = "development", database: str = "github-commit-data"):
        super().__init__(project_name, environment, database)
        self.uuid_collection = USER_SUBMISSION_COLLECTION if environment == "production" else USER_SUBMISSION_COLLECTION

    
    def get_user_submissions(self, uuid: str) -> Dict[str, str]:
        ''' Get users problem submissions

        The structure is 
        1. users_leetcode_submissions
            1. uuid
                1. problems
                    1. problem_id
                        1. last_reviewed_timestamp
                        2. diffculty
                        3. next_review_timestamp
        
        We need to get the subcollections of problems for a user

        Args:
            uuid (str): User ID
        
        Returns:
            Dict: User submissions
        '''
        collection_ref = self.get_collection(self.uuid_collection)
        doc_ref = self.get_doc_ref(collection_ref, uuid)
        try:
            doc = doc_ref.get()
            if doc.exists:
                subcollection_ref = doc_ref.collection('problems')
                docs = subcollection_ref.stream()
                return docs
            else:
                return None
        except Exception as e:
            print(f"Error in get_user_submissions for user {uuid}: {e}")
            raise e
        
    def get_user_submission_for_problem(self, uuid: str, problem_id: str):
        print(f"Adding problem: {problem_id} for user: {uuid}")

        '''
        Get the user's submission for a specific problem
        '''
        collection_ref = self.get_collection(self.uuid_collection)
        doc_ref = self.get_doc_ref(collection_ref, uuid)
        try:
            doc = doc_ref.get()
            if doc.exists:
                subcollection_ref = doc_ref.collection('problems')
                subcollection_doc_ref = subcollection_ref.document(str(problem_id))
                subcollection_doc = subcollection_doc_ref.get()
                print("subcollection_doc:", subcollection_doc.to_dict())
                return subcollection_doc
            else:
                return None
        except Exception as e:
            print(f"Error in get_user_submission_for_problem for user {uuid}: {e}")
            raise e

    def get_all_user_uuids(self) -> list:
        '''
        Get all user uuids
        '''
        collection_ref = self.get_collection(self.uuid_collection)
        print("collection_ref:", collection_ref)
        try:
            docs = list(collection_ref.stream())  # Convert to list to print and see content
            print("Number of documents fetched:", len(docs))
            print("docs:", docs)  # Print documents for debugging
            uuids = [doc.id for doc in docs]
            print("uuids:", uuids)
            return uuids
        except Exception as e:
            print(f"Error in get_all_user_uuids: {e}")
            raise e
    
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
                print("doc", subcollection_doc.to_dict())
                print("updating submission:", update_fields)
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

    def get_problem_past_reviewed_date(self):
        """
        Return:
        {
            uuid1: [prob_id1, prob_id2, ...],
            uuid2: [prob_id3, prob_id4, ...]
        }
        """
        collection_ref = self.get_collection(self.uuid_collection)

        subdocument_refs = collection_ref.list_documents()

        uuid_to_problems_id = {}
        for subdoc_ref in subdocument_refs:
            uuid = subdoc_ref.id
            
            uuid_to_problems_id[uuid] = []

            all_problems = subdoc_ref.collection('problems').stream()
            for prob in all_problems:
                prob = prob.to_dict()
                prob_id = list(prob.keys())[0]
                prob_info = prob.get(prob_id)

                next_review_timestamp = prob_info.get('next_review_timestamp')
                if next_review_timestamp is None or isinstance(next_review_timestamp, str) :
                    continue
                next_review_date = next_review_timestamp.date()
                today = datetime.now().date()

                if next_review_date <= today:
                    uuid_to_problems_id[uuid].append(prob_id)
            

        return uuid_to_problems_id