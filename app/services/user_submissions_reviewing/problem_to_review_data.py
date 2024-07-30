from dataclasses import dataclass, asdict
from typing import Optional
from datetime import datetime as Date

@dataclass
class ProblemToReview:
    problem_id: str = "unknown"
    category: str = "unknown"
    user_rating: int = 3
    last_reviewed_timestamp: Optional[Date] = None
    next_review_timestamp: Optional[Date] = None
    streak: int = 0

    def __str__(self):
        return f"{self.problem_id}. {self.category} (user_rating: {self.user_rating}, last_reviewed_timestamp: {self.last_reviewed_timestamp}, next_review_timestamp: {self.next_review_timestamp}, streak: {self.streak})"
    
    def __repr__(self):
        return self.__str__()

    def __iter__(self):
        for field in asdict(self):
            yield field, getattr(self, field)

    def to_dict(self):
        '''Data is in the format of {problem_id: {problem_data}}'''
        return { self.problem_id : 
            {
            'category': self.category,
            'user_rating': self.user_rating,
            'last_reviewed_timestamp': self.last_reviewed_timestamp,
            'next_review_timestamp': self.next_review_timestamp,
            'streak': self.streak,
            }
        }
    
    def get_problem_id(self):
        return self.problem_id
    
    def get_category(self):
        return self.category
    
    def get_user_rating(self):
        return self.user_rating
    
    def get_last_reviewed_timestamp(self):
        return self.last_reviewed_timestamp
    
    def get_next_review_timestamp(self):
        return self.next_review_timestamp
    
    def get_streak(self):
        return self.streak
    
    def set_problem_id(self, problem_id: str):
        self.problem_id = problem_id

    def set_category(self, category: str):
        self.category = category

    def set_user_rating(self, user_rating: int):
        self.user_rating = user_rating
    
    def set_last_reviewed_timestamp(self, last_reviewed_timestamp: str):
        self.last_reviewed_timestamp = last_reviewed_timestamp

    def set_next_review_timestamp(self, next_review_timestamp: str):
        self.next_review_timestamp = next_review_timestamp

    def set_streak(self, streak: int):
        self.streak = streak

    