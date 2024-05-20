from datetime import datetime


class ProblemRanker:
    def __init__(self, weights):
        self.weights = weights

    def rank_problems(self, problems_data):
        scores = []
        for data in problems_data:
            time_since_last_review = (datetime.now() - data['next_review_date']).days
            ease_factor = data['adjusted_ease']
            interval = data['adjusted_interval']

            score = (self.weights['time'] * time_since_last_review +
                     self.weights['ease'] * (1 - ease_factor) +
                     self.weights['interval'] * (1 / interval))

            scores.append((data['problem_id'], score))

        scores.sort(key=lambda x: x[1], reverse=True)
        return [problem_id for problem_id, score in scores]

