from typing import List, Dict
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

    def get_all_problems_for_user(self, user_id: str) -> List[Dict[str, str]]:
        '''Get all problems for a user

        1. Get all user submissions for a user. User submissions may not contain all information about
        a problem and so we need to make a call to problem_manager to get additional informational

        2. For each problem, get the problem info from the problem manager

        3. Construct a dictionary with the problem info and user submission info and append to list
        
        Args:
            user_id (str): User ID
        
        Returns:
            List of problems for user in the form of a dictionary like problem_data defined above
        
        '''
        problem_docs = self.db.get_user_submissions(user_id)

        problems_for_user = []
        for problem_doc in problem_docs:
            print("problem_doc in get_all_problems_for_user:", problem_doc.to_dict())
            try:
                '''
                TODO: Find better way to abstract this/handle this
                When working with the problem doc, it will always be like


                 Problem doc is in the form of {"id": {problem_data}}.
                 We need to get the problem_data

                 Thats why we do next(iter(problem_doc.values())) to get the problem_data
                
                
                '''
                
                if not problem_doc.exists:
                    continue
                new_problem = {} #todo - Good place to define a proto

                # print("problem_doc:", problem_doc)

                problem_id = str(problem_doc.id)
                new_problem['id'] = problem_id

                problem_doc = problem_doc.to_dict()
                problem = next(iter(problem_doc.values())) # Gets {problem_data}
                print("problem:", problem)

            

                problem_info = self.problem_manager.get_problem_by_id(int(new_problem['id']))

                new_problem['name'] = problem_info.name
                
                if 'difficulty' or 'category' in problem:
                    new_problem['category'] = problem_info.category #todo - rework    


                if 'user_rating' in problem:    #this is an issue   
                    new_problem['user_rating'] = problem['user_rating']

                if 'last_reviewed_timestamp' in problem:
                    new_problem['last_reviewed_timestamp'] = problem['last_reviewed_timestamp']
                
                if 'next_review_timestamp' in problem:
                    new_problem['next_review_timestamp'] = problem['next_review_timestamp']

                new_problem['link'] = problem_info.link

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