from dataclasses import dataclass
from datetime import datetime

@dataclass
class FSRSData:
    '''Data class for storing the data of a problem in the FSRS system.

    Attributes:
        problem_id: str
        ease: float
        interval: int
        next_review_timestamp: datetime
    '''
    problem_id: str
    ease: float
    interval: int
    next_review_timestamp: datetime

    def __str__(self):
        return f"Problem ID: {self.problem_id}, Ease: {self.ease}, Interval: {self.interval}, Next Review Timestamp: {self.next_review_timestamp}"

    def __repr__(self):
        return self.__str__()
    
    def to_dict(self):
        return {
            'problem_id': self.problem_id,
            'ease': self.ease,
            'interval': self.interval,
            'next_review_timestamp': self.next_review_timestamp
        }
    
    def get_problem_id(self):
        return self.problem_id
    
    def get_ease(self):
        return self.ease
    
    def get_interval(self):
        return self.interval
    
    def get_next_review_timestamp(self):
        return self.next_review_timestamp
    
    def set_problem_id(self, problem_id):
        self.problem_id = problem_id

    def set_ease(self, ease):
        self.ease = ease
    
    def set_interval(self, interval):
        self.interval = interval
    
    def set_next_review_timestamp(self, next_review_timestamp):
        self.next_review_timestamp = next_review_timestamp