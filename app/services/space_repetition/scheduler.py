from datetime import datetime

from app.services.space_repetition.fsrs import FSRS
from app.services.space_repetition.fsrs_data import FSRSData

class FSRSScheduler:
    def __init__(self):
        self.fsrs = FSRS()

    def get_next_review_data_for_problem(
            self, 
            problem_id: str, 
            last_review_date: datetime, 
            ease: float, 
            interval: int, 
            performance_rating: int,
        ) -> FSRSData:
        ''' Get the next review data for a problem based on the user's performance rating
        
        Args:
            problem_id (str): The ID of the problem
            last_review_date (datetime): The timestamp of the last review
            ease (float): The current ease value
            interval (int): The current interval. An interval is represented as 
            the number of days between reviews
            performance_rating (int): The user's performance rating on the review
        
        Returns:
            FSRSData: The data for the next review of the problem
        '''

        # Calculate the updated ease and interval based on the performance rating
        # Using the FSRS algorithm
        ease, interval = self.fsrs.schedule_review(
            performance_rating, 
            ease, 
            interval, 
            1.0 # TODO - Dynamically set the factor
        )

        next_review_timestamp = self.fsrs.get_next_review_timestamp(last_review_date, 
                                                                    interval)
        
        return FSRSData(
            problem_id=problem_id,
            ease=ease,
            interval=interval,
            next_review_timestamp=next_review_timestamp
        )


