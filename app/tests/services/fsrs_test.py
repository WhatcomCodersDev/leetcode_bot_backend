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

def test_calculate_next_interval(fsrs: FSRS):
    result = fsrs.calculate_next_interval(ease=2, interval=1, factor=1.0)
    assert result == 2  # 1 * 2 * 1.0

    result = fsrs.calculate_next_interval(ease=1.5, interval=0.5, factor=1.0)
    assert result == 1.5  # 1 (minimum) * 1.5 * 1.0

def test_update_ease(fsrs: FSRS):
    assert round(fsrs.update_ease(ease=2, performance_rating=4), 2) == 2.1
    assert round(fsrs.update_ease(ease=2, performance_rating=3), 2) == 1.9
    assert round(fsrs.update_ease(ease=2, performance_rating=2), 2) == 1.8
    assert round(fsrs.update_ease(ease=1.2, performance_rating=2), 2) == 1.3  # Minimum ease of 1.3

def test_get_next_review_timestamp(fsrs: FSRS):
    last_review_date = datetime(2023, 1, 1)
    interval = 5
    expected_date = last_review_date + timedelta(days=interval)
    result = fsrs.get_next_review_timestamp(last_review_date, interval)
    assert result == expected_date

def test_review(fsrs: FSRS):
    ease, interval = fsrs.schedule_review(performance_rating=4, ease=2, interval=1, factor=1.0)
    assert ease == 2.1
    assert interval == 2.1  # 1 * 2.1 * 1.0

    ease, interval = fsrs.schedule_review(performance_rating=3, ease=2, interval=1, factor=1.0)
    assert ease == 1.9
    assert interval == 1.9  # 1 * 1.9 * 1.0

    ease, interval = fsrs.schedule_review(performance_rating=2, ease=2, interval=1, factor=1.0)
    assert ease == 1.8
    assert interval == 1.8  # 1 * 1.8 * 1.0
