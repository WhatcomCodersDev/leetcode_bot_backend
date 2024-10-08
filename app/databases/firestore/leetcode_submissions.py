# leetcode_manager.py
from google.cloud.firestore_v1 import DocumentSnapshot # type: ignore
from app.databases.firestore.firestore_base import FirestoreBase
from datetime import datetime
from typing import List
from constants import USER_SUBMISSION_COLLECTION
from app.services.user_submissions_reviewing.problem_to_review_data import ProblemToReview

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

class FirestoreSubmissionCollectionWrapper(FirestoreBase):
    def __init__(self, project_name: str, environment: str = "development", database: str = "github-commit-data"):
        super().__init__(project_name, environment, database)
        self.uuid_collection = USER_SUBMISSION_COLLECTION if environment == "production" else USER_SUBMISSION_COLLECTION

    
    def get_user_submissions(self, uuid: str) -> List[DocumentSnapshot]:
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
            DocumentSnapshot: User submissions
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
        
    def get_user_submission_for_problem(self, 
                                        uuid: str, 
                                        problem_id: str,
                                        ) -> ProblemToReview:
        ''' Get the user's submission for a specific problem
        '''
        print(f"Getting problem: {problem_id} for user: {uuid}")
        collection_ref = self.get_collection(self.uuid_collection)
        doc_ref = self.get_doc_ref(collection_ref, uuid)
        try:
            doc = doc_ref.get()
            if doc.exists:
                subcollection_ref = doc_ref.collection('problems')
                subcollection_doc_ref = subcollection_ref.document(str(problem_id))
                subcollection_doc = subcollection_doc_ref.get()

                if subcollection_doc.exists:
                    subcollection_doc = subcollection_doc.to_dict()
                    print("subcollection_doc:", subcollection_doc)
                    
                    return ProblemToReview(problem_id=problem_id, 
                                           **subcollection_doc[problem_id])
                else:
                    return None
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
                                   problem_to_review: ProblemToReview,
                                   ):
        '''
        1. Get the user's submission document by uuid
        2. If user's submission document doesn't exist, create it with the initial submission
        3. Else, update the submission with the new submission data

        Note: Submission could be an attempt or solving the problem. We always assume
        at least one is not None, so we can update the submission

        This means that one timestamp will remain the same, while the other will be updated
        '''
                                  
        # Get the user's submission collection: https://console.cloud.google.com/firestore/databases/github-commit-data/data/panel/users_leetcode_submissions?project=gothic-sled-375305
        collection_ref = self.get_collection(self.uuid_collection)

        # Get the user's submission document based on uuid if it exists
        doc_ref = self.get_doc_ref(collection_ref, uuid)
        
        # Check if the uuid exists otherwise create it
        doc = doc_ref.get()
        if not doc.exists:
            print(f"User {uuid} doesn't exist in the db. Creating a new document for them.")
            doc_ref.set({})

        # Now create/update the problem sub collection
        try:
            # Get the subcollection of problems for the user
            subcollection_ref = doc_ref.collection('problems')
            # Get the document reference for the specific problem
            subcollection_doc_ref = subcollection_ref.document(str(problem_id))
        except Exception as e:
            print(f"Error in update_leetcode_submission for user {uuid} in phase 1: {e}")
            raise e


        try:
            # Get the document for the specific problem
            subcollection_doc = subcollection_doc_ref.get()

            # Check if the document for the problem submission exists
            if subcollection_doc.exists:
                print("doc", subcollection_doc.to_dict())
                print("updating submission:", problem_to_review)
                # Document exists, so we update it, specifically last_asked-timestamp
                subcollection_doc_ref.update(problem_to_review)
                print(f"Updated submission for problem #{problem_id} for user {uuid}.")
            else:
                # Document doesn't exist, so we create it with the initial user in users_solved
               
                subcollection_doc_ref.set(problem_to_review) #todo - make problems a constant
                print(f"Submission for problem #{problem_id} added successfully to the db for user {uuid}")
                
        except Exception as e:
            print(f"Error in update_leetcode_submission for user {uuid} in phase 2: {e}")
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