import pytz

from datetime import datetime, timedelta
from typing import List, Dict 
from app.databases.firestore.leetcode_submissions import FirestoreSubmissionCollectionWrapper
from app.databases.firestore.leetcode_reviewTypes import FirestoreUsersLeetcodeReviewCategoriesCollectionWrapper
from app.services.space_repetition.scheduler import FSRSScheduler, FSRSData
from app.services.user_submissions_reviewing.problem_to_review_data import ProblemToReview
from app.services.time_utils import make_aware, make_naive
from constants import REVIEW_CATEGORY_KEY, REVIEWED_EASE, FAILED_EASE
from google.cloud.firestore_v1 import DocumentSnapshot # type: ignore


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


    def process_user_reviews(self, user_id: str) -> None:
        ''' Process the reviews for a user

        Args:
            user_id (str): The user id to process the reviews for

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
                if not problem_to_review.get_next_review_timestamp():
                    problem_to_review.set_next_review_timestamp(make_aware(datetime.now()))

                timewindow_in_memory = problem_to_review.get_next_review_timestamp() + timedelta(days=1)
                review_count += self.handle_review_logic(user_id, problem_to_review, timewindow_in_memory)
            if review_count == len(problems_to_review):
                print("TODO - Add a new problem for that review category")


    def get_user_problems_by_category(self, 
                                      user_id: str,
                                      ) -> Dict[str, List[ProblemToReview]]:
        ''' Get all the problems for a user grouped by category
        
        1. Get all the problem submissions for a user
        2. Get the problem categories marked for review by the user
        3. Create a map of problem categories to problems

        Args:
            user_id (str): The user id to get the problems for
        
        Returns:
            A map of problem categories to problems

        Ex: {'Binary Search': [problem1, problem2], 'DFS': [problem1, problem2]}
        '''
        user_problems = self.firestore_submission_collection_wrapper.get_user_submissions(user_id)
        user_review_categories = self.firestore_leetcode_review_type_wrapper.get_problem_categories_marked_for_review_by_user(user_id)
        if user_review_categories:
            user_review_categories = user_review_categories[REVIEW_CATEGORY_KEY]
        else:
            print(f"No review categories found for user {user_id}")
            user_review_categories = {}
        return self.create_problem_category_to_problem_map(user_problems, user_review_categories)

    def create_problem_category_to_problem_map(self, 
                                               user_problems: List[DocumentSnapshot], 
                                               user_review_categories: Dict[str, str],
                                               ) -> Dict[str, List[ProblemToReview]]:
        '''Create a map of problem categories to problems

        Args:
            user_problems (List[DocumentSnapshot]): The user's problems
            user_review_categories (Dict[str, str]): The categories marked for review by the user
        
        Returns:
            A map of problem categories to problems

        user_review_categories = {'Binary Search', 'DFS'}
        create map that is like {'Binary Search': [problem1, problem2], 'DFS': [problem1, problem2]}

        '''
        user_problems_by_category = {}

        # Iterate through the Firestore DocumentSnapshot objects
        for problem_doc in user_problems:
            problem_id = problem_doc.id
            # Gets the outer dictionary containing the problem data
            # Ex: Problem data: {'127': {'last_reviewed_timestamp': datetime.datetime(2024, 7, 30, 5, 47, 0, 762358), 'user_rating': 3, 'next_review_timestamp': None, 'streak': 0, 'category': 'Binary Search'}}
            problem_data = problem_doc.to_dict()
            # Extract the inner dictionary containing the actual problem data
            problem_data = next(iter(problem_data.values()))

            # Initialize ProblemToReview with problem data
            problem_to_review = ProblemToReview(problem_id=problem_id, **problem_data)

            # Retrieve and check the problem's category
            category = problem_to_review.get_category()
            if category and category in user_review_categories:
                # Add problem to the appropriate category list
                if category not in user_problems_by_category:
                    user_problems_by_category[category] = []
                user_problems_by_category[category].append(problem_to_review)
        
        return user_problems_by_category

    def update_review_date(self, 
                           user_id: str, 
                           problem_to_review: ProblemToReview, 
                           review_data: FSRSData,
                           ):
        problem_to_review = ProblemToReview(
            problem_id=problem_to_review.get_problem_id(),
            category=problem_to_review.get_category(),
            user_rating=problem_to_review.get_user_rating(),
            last_reviewed_timestamp=problem_to_review.get_last_reviewed_timestamp(),
            next_review_timestamp=review_data.get_next_review_timestamp(),
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
        print("problem_to_review:", problem_to_review)
        if not problem_to_review.get_last_reviewed_timestamp():
            # If the problem has not been reviewed yet, skip the review logic
            print(f"Problem {problem_to_review.get_problem_id()} has not been reviewed yet")
            return review_count
        try:
            if self.timewindow_not_open_yet(problem_to_review):
                print("Case 1: Time window hasn't opened")

            elif self.user_reviewed_problem_within_timewindow(problem_to_review, timewindow_in_memory):
                print("Case 2: This user has successfully reviewed the problem within the time window")
                review_data = self.fsrs_scheduler.get_next_review_data_for_problem(
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
            elif self.user_failed_to_review_problem_within_timewindow(problem_to_review, timewindow_in_memory):
                print("Case 3: This user has failed to review the problem within the time window")
                review_data = self.fsrs_scheduler.get_next_review_data_for_problem(
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
    
            else:
                print("Case 4: No case matched")
        except Exception as e:
            print(f"Error in updating review for user {user_id} and problem {problem_to_review.get_problem_id()}: {e}")
        return review_count

    def timewindow_not_open_yet(self, 
                    problem_to_review: ProblemToReview,
                    ):
        '''Case 1: Time window hasn't opened
        
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
    

    def user_reviewed_problem_within_timewindow(self, 
                    problem_to_review: ProblemToReview,
                    timewindow_in_memory: datetime,
                    ):
        '''Case 2: This user has successfully reviewed the problem within the time window
        
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

    def user_failed_to_review_problem_within_timewindow(self, 
                    problem_to_review: ProblemToReview, 
                    timewindow_in_memory: datetime,
                    ):
        '''Case 3: This user has failed to review the problem within the time window
        
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
