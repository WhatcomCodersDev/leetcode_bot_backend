from datetime import timedelta, datetime
from typing import Tuple 

'''
The FSRS algorithm is an advanced spaced repetition algorithm 
that adjusts the review schedule dynamically based on user feedback 
and retention rates. 

It often uses a more complex formula to optimize the intervals 
between reviews, aiming for an efficient balance between memory retention 
and the number of reviews needed.

'''

class FSRS:
    ''' Implementation of the Free Spaced Repetition Scheduler algorithm
    

    The algorithm schedules reviews based on the performance of the user on the previous review. 
    The algorithm uses three main parameters to calculate the next review interval:
    1. Ease - A factor that adjusts the interval based on the user's performance 
    on the previous review
    2. Interval - The time between the last review and the next review
    3. Factor: A factor that adjusts the interval based on the user's performance on 
    the previous review

    The algorithm uses the following formula to calculate the next interval:
    next_interval = interval * ease * factor

    The algorithm also adjusts the ease based on the user's performance on the previous review:
    - If the user's performance is 4 or higher, the ease is increased by 0.1
    - If the user's performance is 3, the ease is decreased by 0.1
    - If the user's performance is 2 or lower, the ease is decreased by 0.2
    - The ease is capped at a minimum value of 1.3

    Performance_rating: TODO - Make to ENUM
        0 - Forgotten
        1 - Super Easy
        2 - Easy
        3 - Medium
        4 - High-Medium
        5 - Hard

    The algorithm schedules the next review based on the last review date and the calculated interval:
    next_review_timestamp = last_review_date + interval
    
    '''
    def __init__(self, 
                 initial_ease: float = 1.0, 
                 initial_interval: int = 1, 
                 initial_factor: float = 1.0,
                 ):
        self.initial_ease = initial_ease
        self.initial_interval = initial_interval
        self.initial_factor = initial_factor

    def schedule_review(self, 
               performance_rating: int, 
               ease: float, 
               interval: int, 
               factor: float,
               ) -> Tuple[float, int]:
        ''' Perform a review and calculate the updated ease and interval
        
        Args:
            performance_rating (int): The user's performance rating on the review
            ease (float): The current ease value
            interval (int): The current interval. An interval is represented as 
            the number of days between reviews
            factor (float): The current factor

        Returns:
            tuple: A tuple containing the updated ease and interval
        '''
        ease = round(self.update_ease(ease, performance_rating), 2)
        interval = round(self.calculate_next_interval(ease, interval, factor), 2)
        return ease, interval

    def get_next_review_timestamp(
            self, 
            last_review_date: datetime, 
            interval: int,
        ) -> datetime:
        ''' Calculate the date of the next review based on the last review date and interval
        
        Args:
            last_review_date (datetime): The date of the last review
            interval (int): The interval between the last review and the next review

        Returns:
            datetime: The date of the next review
        '''
        next_review_timestamp = last_review_date + timedelta(days=interval)
        return next_review_timestamp


    def calculate_next_interval(
            self, 
            ease: float, 
            interval: int, 
            factor: float,
        ) :
        # Adjust interval calculation to keep initial intervals short
        if interval < 1:
            interval = 1  # Ensuring minimum interval of 1 day
        next_interval = interval * ease * factor
        return next_interval

    def update_ease(
            self, 
            ease: float, 
            performance_rating: int
        ) -> float:
        ''' Update the ease based on the user's performance on the previous review
        
        Args:
            ease (float): The current ease value
            performance_rating (int): The user's performance rating on the previous review
        
        Returns:
            float: The updated ease value
        '''
        if performance_rating >= 4:
            ease += 0.1
        elif performance_rating == 3:
            ease -= 0.1
        elif performance_rating <= 2:
            ease -= 0.2
        elif performance_rating == 0:
            ease = 1.3

        if ease < 1.3:
            ease = 1.3

        return ease
