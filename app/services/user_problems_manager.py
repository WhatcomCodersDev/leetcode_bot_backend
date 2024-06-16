from typing import List, Dict
from datetime import datetime
from app.services.databases.firestore.leetcode_submissions import SubmissionCollectionManager
from app.services.problem_manager import ProblemManager

problem_data = {
    'id': None,
    'name': None,
    'user_rating': None,
    'category': None,
    'last_review_timestamp': None,
    'next_review_timestamp': None,
}

class UserProblemManager:
    def __init__(self, db: SubmissionCollectionManager, problem_manager: ProblemManager):
        self.db = db
        self.problem_manager = problem_manager

    def get_all_problems_for_user(self, user_id: str) -> list:
        '''Get all problems for a user'''
        problem_docs = self.db.get_user_submissions(user_id)
        # print("problem_docs:", problem_docs)

        problems_for_user = []
        for problem_doc in problem_docs:
            print("problem_doc:", problem_doc.to_dict())
            try:
                new_problem = {} #todo - Good place to define a proto

                # print("problem_doc:", problem_doc)

                problem_id = str(problem_doc.id)
                print("this is problem id", problem_id)
                new_problem['id'] = problem_id

                if not problem_doc.exists:
                    continue

                problem_doc = problem_doc.to_dict()
                # print("problem_doc:", problem_doc)
                problem_info = self.problem_manager.get_problem_by_id(int(new_problem['id']))

                new_problem['name'] = problem_info.name
                
                if 'difficulty' or 'category' in problem_doc:
                    new_problem['category'] = problem_info.category #todo - rework    


                if 'user_rating' in problem_doc:    #this is an issu   
                    new_problem['user_rating'] = problem_doc['user_rating']

                if 'last_reviewed_timestamp' in problem_doc:
                    new_problem['last_reviewed_timestamp'] = problem_doc['last_reviewed_timestamp']
                
                if 'next_review_timestamp' in problem_doc:
                    new_problem['next_review_timestamp'] = problem_doc['next_review_timestamp']

                problems_for_user.append(new_problem)
            except Exception as e:
                print(f"Error in get_all_problems_for_user for user {user_id}: {e}")
                continue

        return problems_for_user

    def update_user_review_problems(self, user_id: str, data: List[Dict[str, str]]):
        '''Update users review problems'''
        if not data:
            print('No data provided')
            return {'error': 'No data provided'}, 400
        
        if not user_id:
            return {'error': 'User ID not provided'}, 400

        for problem_data in data:
            if not problem_data:
                print('Problem data not provided')
                return {'error': 'Problem data not provided'}, 400

            try:
                problem_data = {str(problem_data['id']): problem_data}
                self.db.update_leetcode_submission(user_id, str(problem_data['id']), problem_data)
            except Exception as e:
                print(f"Error in update_user_problems for user {user_id}: {e}")
                return {'error': e}, 500

        return {'message': 'Success'}, 200