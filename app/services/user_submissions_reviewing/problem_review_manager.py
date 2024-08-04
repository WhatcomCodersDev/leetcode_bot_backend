from datetime import datetime, timedelta
from typing import List, Dict 
from app.databases.firestore.leetcode_submissions import FirestoreSubmissionCollectionWrapper
from app.databases.firestore.leetcode_reviewTypes import FirestoreUsersLeetcodeReviewCategoriesCollectionWrapper
from app.services.space_repetition.scheduler import FSRSScheduler
from app.services.user_submissions_reviewing.problem_to_review_data import ProblemToReview
from app.services.time_utils import make_aware, make_naive
from constants import REVIEW_CATEGORY_KEY, REVIEWED_EASE, FAILED_EASE


class ProblemReviewManager:
    ''' Class to manage the review of problems for a user'''
    def __init__(self, 
                 firestore_submission_collection_wrapper: FirestoreSubmissionCollectionWrapper, 
                 firestore_leetcode_review_type_wrapper: FirestoreUsersLeetcodeReviewCategoriesCollectionWrapper, 
                 fsrs_scheduler: FSRSScheduler,
                 ):
        self.firestore_submission_collection_wrapper = firestore_submission_collection_wrapper
        self.firestore_leetcode_review_type_wrapper = firestore_leetcode_review_type_wrapper
        self.fsrs_scheduler = fsrs_scheduler

    def __get_all_user_uuids__(self):
        return self.firestore_submission_collection_wrapper.get_all_user_uuids()


    def process_user_reviews(self, user_id):
        '''
        1. Fetch all collections from users_problemtypes_for_review collection
        2. For each collection, iterate through each problem types
        3. For each problem in problem category, update the review_date
            if the review date has passed and the user has reviewed the problem then the review date should increase
            if the review date has passed and the user has not reviewed the problem then the review date should decrease
            there may exist a middle option. The spaced repetition algorithm should be used to determine the next review date
        4. Update the review date in the document
        
        5. If the user has reviewed all problem for that problem category, and the review dates are all
        above a week, then add a new problem category to the user's review types
        


        {uuid:
            dP: {problem 1, problem 2, problem 3}
            DFS: {problem 1, problem 2, problem 3}
        
        uuid2
            
        }

        Alternatively:
        
        Get and create some Metadata
        1. Fetch the problemtypes collection
        2. Load all problem data in a hashmap
            1. Keep a map of problem types to problems


        1. Iterate through each users leetcode submissions
            1. Filter and group the problems by problem category
            2. Iterate through each problem in the problem category
                1. Do the logic as before

                
        Actually, use submission manager to fetch the problems and filter by 'category' field

        '''
        user_problems_by_category = self.get_user_problems_by_category(user_id)
        for review_category, problems_to_review in user_problems_by_category.items():
            review_count = 0
            for problem_to_review in problems_to_review:
                if 'next_review_timestamp' not in problem_to_review:
                    problem_to_review.set_next_review_timestamp(make_aware(datetime.now()))
                timewindow_in_memory = problem_to_review.get_next_review_timestamp() + timedelta(days=1)
                review_count += self.handle_review_logic(user_id, problem_to_review, timewindow_in_memory)
            if review_count == len(problems_to_review):
                print("TODO - Add a new problem for that review category")


    def get_user_problems_by_category(self, user_id) -> Dict[str, List[ProblemToReview]]:
        user_problems = self.firestore_submission_collection_wrapper.get_user_submissions(user_id)
        user_review_categories_list = self.firestore_leetcode_review_type_wrapper.get_problem_categories_marked_for_review_by_user(user_id)
        user_review_categories = user_review_categories_list[REVIEW_CATEGORY_KEY]
        return self.create_problem_category_to_problem_map(user_problems, user_review_categories)

    def create_problem_category_to_problem_map(self, 
                                               user_problems, 
                                               user_review_categories,
                                               ) -> Dict[str, List[ProblemToReview]]:
        '''
        Create a map of problem categories to problems

        user_review_categories = {'Binary Search', 'DFS'}
        create map that is like {'Binary Search': [problem1, problem2], 'DFS': [problem1, problem2]}

        '''
        user_problems_by_category = {}
        # iterate through firestore snapshot
        for problem_generator in user_problems:
            problem = problem_generator
            print("problem:", problem)
            problem_id = problem_generator.id
            problem_data = next(iter(problem.to_dict().values()))
            print("problem:", problem_data)

            problem_to_review = ProblemToReview(problem_id=problem_id, **problem_data)

            print("problem_id:", problem_id)
            # problem = problem.to_dict() # Gets {'1': {problem_data}}
            if problem_to_review.category and problem_to_review.get_category() in user_review_categories:
                if problem_to_review.get_category() not in user_problems_by_category:
                    user_problems_by_category[problem_to_review.get_category()] = []
                user_problems_by_category[problem_to_review.get_category()].append(problem_to_review)
        
        print("user_problems_by_category:", user_problems_by_category)
        return user_problems_by_category

    def update_review_date(self, 
                           user_id: str, 
                           problem_to_review: ProblemToReview, 
                           review_data: Dict[str, datetime],
                           ):
        problem_to_review = ProblemToReview(
            problem_id=problem_to_review.get_problem_id(),
            category=problem_to_review.get_category(),
            user_rating=problem_to_review.get_user_rating(),
            last_reviewed_timestamp=problem_to_review.get_last_reviewed_timestamp(),
            next_review_timestamp=review_data['next_review_timestamp'],
            streak=problem_to_review.get_streak(),
        )
        self.firestore_submission_collection_wrapper.update_leetcode_submission(
            user_id, 
            problem_to_review.get_problem_id(), 
            problem_to_review.to_dict(),
        )


    def handle_review_logic(self, 
                            user_id: str, 
                            problem_to_review: ProblemToReview, 
                            timewindow_in_memory: datetime,
                            ):
        review_count = 0
        if not problem_to_review.get_last_reviewed_timestamp():
            problem_to_review.set_next_review_timestamp(datetime.now())
        try:
            if self.case1_logic(problem_to_review, timewindow_in_memory):
                print("Case 1: This user has successfully reviewed the problem within the time window")
                review_data = self.fsrs_scheduler.schedule_review(
                    problem_to_review.get_problem_id(), 
                    datetime.now(), 
                    ease=REVIEWED_EASE, 
                    interval=1, 
                    performance_rating=problem_to_review.get_user_rating()
                )
                self.update_review_date(user_id, 
                                        problem_to_review, 
                                        review_data, 
                                        )
                review_count += 1
            elif self.case2_logic(problem_to_review, timewindow_in_memory):
                print("Case 2: This user has failed to review the problem within the time window")
                review_data = self.fsrs_scheduler.schedule_review(
                    problem_to_review.get_problem_id(), 
                    datetime.now(), 
                    ease=FAILED_EASE, 
                    interval=1, 
                    performance_rating=2,
                )
                self.update_review_date(
                    user_id, 
                    problem_to_review, 
                    review_data,
                )
            elif self.case3_logic(problem_to_review):
                print("Case 3: Time window hasn't opened")
            else:
                print("Case 4: No case matched")
        except Exception as e:
            print(f"Error in updating review for user {user_id} and problem {problem_to_review.get_problem_id()}: {e}")
        return review_count

    def case1_logic(self, 
                    problem_to_review: ProblemToReview,
                    timewindow_in_memory: datetime,
                    ):
        '''Case 1: This user has successfully reviewed the problem within the time window
        
            last_reviewed: july 10 12pm
            next_reviewed: july 10 10am
            time_window: july 11  


            Conditions
            1. The current time is within the time window (between next_reviewed and time_window)
            2. The last_reviewed is within the time_window

            Current Time: july 10 - july 11  


                |-----------------|-----------------|
            next_reviewed    last_reviewed    time_window
        '''

        return problem_to_review.get_next_review_timestamp() and (datetime.now() >= make_naive(problem_to_review.get_next_review_timestamp()) and datetime.now() < make_naive(timewindow_in_memory)) \
            and (problem_to_review.get_last_reviewed_timestamp() >= problem_to_review.get_next_review_timestamp() and problem_to_review.get_last_reviewed_timestamp() < timewindow_in_memory)

    def case2_logic(self, 
                    problem_to_review: ProblemToReview, 
                    timewindow_in_memory: datetime,
                    ):
        '''Case 2: This user has failed to review the problem within the time window
        
            last_reviewed: july 6
            next_reviewed: july 10
            time_window: july 11

            Conditions
            1. We were in the time window and it has finished (current time is after next_reviewed and time_window)
            2. The last_reviewed is not within the time_window
                
            
            Current Time: july 11 (after time window)

                |-----------------|-----------------|
             last_reviewed    next_reviewed    time_window/current_time
        
        '''
        return problem_to_review.get_next_review_timestamp() and (datetime.now() >= make_naive(problem_to_review.get_next_review_timestamp()) and datetime.now() < make_naive(timewindow_in_memory)) \
            and (problem_to_review.get_last_reviewed_timestamp() < problem_to_review.get_next_review_timestamp() and problem_to_review.get_last_reviewed_timestamp() < timewindow_in_memory)

    def case3_logic(self, 
                    problem_to_review: ProblemToReview,
                    ):
        '''Case 3: Time window hasn't opened
        
            last_reviewed: july 6
            next_reviewed: july 10
            time_window: july 11

            Conditions
            1. The current time is before the next_reviewed

            Current Time: july 9

                |---------------------|------------------|------------------|
             last_reviewed      current_time       next_reviewed       time_window
        
        '''
        return problem_to_review.get_next_review_timestamp() and datetime.now() < make_naive(problem_to_review.get_next_review_timestamp())
    