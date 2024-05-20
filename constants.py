PROBLEM_SHEET_PATH = 'problem_sheet.csv'

# point system
SUBMIT = 0
ATTEMPTED = 1
MEDIUM_PT = 4.0
EASY_PT = 2.0
ATTEMPT_PT = 1.0

# document properties/fields
TITLE = "title"
TIMESTAMP = "last_solved_timestamp"
USERS_SOLVED = "users_solved"
USER_ID = "user_id"
USER_SCORES = "user_scores"

# firestore collection
LEETCODE_COLLECTION = "leetcode_questions"
LEADERBOARD_COLLECTION = "leetcode_leaderboard"
UUID_COLLECTION = "uuid_mapping"
USER_SUBMISSION_COLLECTION = "users_leetcode_submissions"
TEST_LEETCODE_COLLECTION = "test_leetcode_questions"
TEST_LEADERBOARD_COLLECTION = "test_leetcode_leaderboard"

# question duration
TTL = 300
QUESTION_TTL_SECONDS = 604800
TEST_QUESTION_TTL_SECONDS = 10

# redis cache key
REDIS_SOLVED_KEY = 'solved'
REDIS_ATTEMPTED_KEY = 'attempted'
REDIS_EASY_PROBLEM_ID_KEY = 'easy_problem_id'
REDIS_MEDIUM_PROBLEM_ID_KEY = 'medium_problem_id'