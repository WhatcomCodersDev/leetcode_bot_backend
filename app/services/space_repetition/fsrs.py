from datetime import timedelta

class FSRS:
    def __init__(self, initial_ease=2.5, initial_interval=1, initial_factor=1.3):
        self.initial_ease = initial_ease
        self.initial_interval = initial_interval
        self.initial_factor = initial_factor
    
    def calculate_next_interval(self, ease, interval, factor):
        next_interval = interval * ease * factor
        return next_interval

    def update_ease(self, ease, performance_rating):
        # Todo - Make sure input is an int before passing
        performance_rating = int(performance_rating)
        if performance_rating >= 4:
            ease += 0.1
        elif performance_rating == 3:
            ease -= 0.1
        elif performance_rating <= 2:
            ease -= 0.2

        if ease < 1.3:
            ease = 1.3

        return ease

    def schedule_review(self, last_review_date, interval):
        next_review_timestamp = last_review_date + timedelta(days=interval)
        return next_review_timestamp

    def review(self, performance_rating, ease, interval, factor):
        ease = self.update_ease(ease, performance_rating)
        interval = self.calculate_next_interval(ease, interval, factor)
        return ease, interval


