PROBLEM_SHEET_PATH = 'app/services/problem_sheet/sheets/new_problem_sheet.csv'


# document properties/fields
TITLE = "title"
TIMESTAMP = "last_solved_timestamp"
USERS_SOLVED = "users_solved"
USER_ID = "user_id"
USER_SCORES = "user_scores"

# firestore collection
LEETCODE_COLLECTION = "leetcode_questions"
LEADERBOARD_COLLECTION = "leetcode_leaderboard"
USER_PROBLEM_TYPES_FOR_REVIEW_COLLECTION = "users_problemtypes_for_review"
UUID_COLLECTION = "uuid_mapping"
USER_SUBMISSION_COLLECTION = "users_leetcode_submissions"
TEST_LEETCODE_COLLECTION = "test_leetcode_questions"
TEST_LEADERBOARD_COLLECTION = "test_leetcode_leaderboard"

# user submissions and reviewing
REVIEW_CATEGORY_KEY = 'review_types' # Key for the review types in the firestore document
REVIEWED_EASE = 2
FAILED_EASE = 1

# redis
TTL = 300

