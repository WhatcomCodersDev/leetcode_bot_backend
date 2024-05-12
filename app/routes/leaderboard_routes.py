# Routes that handle getting/setting data for leaderboard
'''
1. Get user score
2. Get top n users
3. Add or update user score

'''

from flask import Blueprint, request, jsonify
from app.services import leaderboard_manager

bp = Blueprint('leaderboard', __name__, url_prefix='/leaderboard')
