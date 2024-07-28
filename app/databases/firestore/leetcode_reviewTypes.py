from app.databases.firestore.firestore_base import FirestoreBase
from typing import Dict, Set
from constants import USER_PROBLEM_TYPES_FOR_REVIEW_COLLECTION

'''
Handles interaction with users_problemtypes_for_review collection

Collection: users_problemtypes_for_review


Description: Stores data related to users review types for leetcode questions
Document ID: user_id (uuid)
Fields:
    - review_types (set): Set of review types that the user has marked for review


'''

class FirestoreUsersLeetcodeReviewCategoriesCollectionWrapper(FirestoreBase):
    def __init__(self, project_name: str, environment: str = "development", database: str = "github-commit-data"):
        super().__init__(project_name, environment, database)
        self.uuid_collection = USER_PROBLEM_TYPES_FOR_REVIEW_COLLECTION if environment == "production" else USER_PROBLEM_TYPES_FOR_REVIEW_COLLECTION

    def get_problem_categories_marked_for_review_by_user(self, uuid: str) -> Dict[str, str]:
        ''' Get problem category marked for review by user, for example a user wants to review "BFS" and "DFS" problems
        The structure is 
        1. users_problemtypes_for_review
            1. uuid
                1. review_types
                    1. review_type

        Args:
            uuid (str): User ID
        
        Returns:
            Dict: User review types
        '''
        collection_ref = self.get_collection(self.uuid_collection)
        doc_ref = self.get_doc_ref(collection_ref, uuid)
        try:
            doc = doc_ref.get()
            if doc.exists:
                return doc.to_dict()
            else:
                return None
        except Exception as e:
            print(f"Error in get_problem_categories_marked_for_review_by_user for user {uuid}: {e}")
            raise e
        
    def get_all_user_review_types(self):
        '''
        Get all user review types
        '''
        collection_ref = self.get_collection(self.uuid_collection)
        try:
            docs = collection_ref.stream()
            return {doc.id: doc.to_dict() for doc in docs}
        except Exception as e:
            print(f"Error in get_all_user_review_types: {e}")
            raise e
    
    
    def update_user_problem_categories_marked_for_review(self, uuid: str, review_types: Set[str]) -> None:
        ''' Update user review types for a user

        1. Get the user's review types document by uuid
        2. If user's review types document doesn't exist, create it with the initial review types
        3. Else, update the review types with the new review types

        Args:
            uuid (str): User ID
            review_types (Set[str]): Set of review types that the user has marked for review
        
        

        '''
        collection_ref = self.get_collection(self.uuid_collection)
        doc_ref = self.get_doc_ref(collection_ref, uuid)
        try:
            # Get the user's review types document
            doc = doc_ref.get()
        except Exception as e:
            print(f"Error in update_user_review_types for user {uuid}: {e}")
            raise e

        try:
            if doc.exists:
                # Document exists, so we update it, specifically review_types
                doc_ref.update({'review_types': review_types})
                print(f"Updated review types for user {uuid}.")
            else:
                # Document doesn't exist, so we create it with the initial user in users_solved
                doc_ref.set({'review_types': review_types})
                print(f"Review types added successfully to the db for user {uuid}")
        except Exception as e:
            print(f"Error in update_user_review_types for user {uuid}: {e}")
            raise e
    