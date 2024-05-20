from datetime import datetime

from app.services.space_repetition.fsrs import FSRS

class FSRSScheduler:
    def __init__(self):
        self.fsrs = FSRS()

    def schedule_review(self, 
                        problem_id, 
                        last_review_date, 
                        ease, 
                        interval, 
                        performance_rating):
        ease, interval = self.fsrs.review(performance_rating, ease, interval, 1.3)
        next_review_date = self.fsrs.schedule_review(last_review_date, interval)
        return {
            'problem_id': problem_id,
            'ease': ease,
            'interval': interval,
            'next_review_date': next_review_date
        }
