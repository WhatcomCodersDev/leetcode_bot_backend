import pytest
from datetime import datetime, timedelta
from app.services.space_repetition.fsrs import FSRS

@pytest.fixture
def fsrs():
    return FSRS()

def test_initialization(fsrs):
    assert fsrs.initial_ease == 1
    assert fsrs.initial_interval == 1
    assert fsrs.initial_factor == 1

def test_calculate_next_interval(fsrs):
    result = fsrs.calculate_next_interval(ease=2, interval=1, factor=1.5)
    assert result == 3  # 1 * 2 * 1.5

    result = fsrs.calculate_next_interval(ease=1.5, interval=0.5, factor=2)
    assert result == 3  # 1 (minimum) * 1.5 * 2

def test_update_ease(fsrs):
    assert fsrs.update_ease(ease=2, performance_rating=4) == 2.1
    assert fsrs.update_ease(ease=2, performance_rating=3) == 1.9
    assert fsrs.update_ease(ease=2, performance_rating=2) == 1.8
    assert fsrs.update_ease(ease=1.2, performance_rating=2) == 1.3  # Minimum ease of 1.3

def test_schedule_review(fsrs):
    last_review_date = datetime(2023, 1, 1)
    interval = 5
    expected_date = last_review_date + timedelta(days=interval)
    result = fsrs.schedule_review(last_review_date, interval)
    assert result == expected_date

def test_review(fsrs):
    ease, interval = fsrs.review(performance_rating=4, ease=2, interval=1, factor=1.5)
    assert ease == 2.1
    assert interval == 3.15  # 1 * 2.1 * 1.5

    ease, interval = fsrs.review(performance_rating=3, ease=2, interval=1, factor=1.5)
    assert ease == 1.9
    assert interval == 2.85  # 1 * 1.9 * 1.5

    ease, interval = fsrs.review(performance_rating=2, ease=2, interval=1, factor=1.5)
    assert ease == 1.8
    assert interval == 2.7  # 1 * 1.8 * 1.5
