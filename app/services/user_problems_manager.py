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
            try:
                new_problem = {} #todo - Good place to define a proto

                # print("problem_doc:", problem_doc)

                problem_id = problem_doc.id
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


                if 'user_rating' in problem_doc[str(problem_id)]:    #this is an issu   
                    new_problem['user_rating'] = problem_doc[str(problem_id)]['user_rating']

                if 'last_reviewed_timestamp' in problem_doc[str(problem_id)]:
                    new_problem['last_reviewed_timestamp'] = problem_doc[str(problem_id)]['last_reviewed_timestamp']
                
                if 'next_review_timestamp' in problem_doc[str(problem_id)]:
                    new_problem['next_review_timestamp'] = problem_doc[str(problem_id)]['next_review_timestamp']

                problems_for_user.append(new_problem)
            except Exception as e:
                print(f"Error in get_all_problems_for_user for user {user_id}: {e}")
                continue

        return problems_for_user