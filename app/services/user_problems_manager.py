from datetime import datetime
from app.services.databases.firestore.leetcode_submissions import SubmissionCollectionManager
from app.services.problem_manager import ProblemManager

problem_data = {
    'id': None,
    'name': None,
    'difficulty': None,
    'problem_type': None,
    'last_asked_timestamp': None,
    'next_review_date': None,
}

class UserProblemManager:
    def __init__(self, db: SubmissionCollectionManager, problem_manager: ProblemManager):
        self.db = db
        self.problem_manager = problem_manager

    def get_all_problems_for_user(self, user_id: str) -> list:
        '''Get all problems for a user'''
        problem_docs = self.db.get_user_submissions(user_id)
        print("problem_docs:", problem_docs)

        problems_for_user = []

        new_problem = {} #todo - Good place to define a proto

        for problem_doc in problem_docs:
            print("problem_doc:", problem_doc)

            new_problem['id'] = problem_doc.id

            if not problem_doc.exists:
                continue
            problem_doc = problem_doc.to_dict()
            print("problem_doc:", problem_doc)
            problem_info = self.problem_manager.get_problem_by_id(int(new_problem['id']))

            new_problem['name'] = problem_info.name
            new_problem['problem_type'] = problem_info.tag #todo - rework     

            if 'difficulty' in problem_doc:    #this is an issu   
                new_problem['difficulty'] = problem_doc['difficulty']

            if 'last_asked_timestamp' in problem_doc:
                new_problem['last_attempt_timestamp'] = problem_doc['last_attempt_timestamp']
            
            if 'next_review_timestamp' in problem_doc:
                new_problem['next_review_timestamp'] = problem_doc['next_review_timestamp']

            problems_for_user.append(new_problem)

        return problems_for_user