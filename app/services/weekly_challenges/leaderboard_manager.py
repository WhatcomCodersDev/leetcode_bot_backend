from constants import ATTEMPT_PT, EASY_PT, MEDIUM_PT, TTL, QUESTION_TTL_SECONDS, REDIS_SOLVED_KEY, REDIS_ATTEMPTED_KEY
from app.services.databases.redis.redis_client import RedisClient
from app.services.databases.firestore.leaderboard import LeaderboardCollectionManager
from typing import Dict, List, Optional
from datetime import datetime
from util import get_ttl_for_next_monday_9am


class LeaderboardManager:
    def __init__(self, 
                 firestore_client: LeaderboardCollectionManager, 
                 redis_client: RedisClient):
        self.firestore_client = firestore_client
        self.redis_client = redis_client

    # NOTE: problem_difficulty must in lower case
    def process_points_for_submission(self, 
                                      question_id: str, 
                                      question_title:str, 
                                      user_id: str, 
                                      problem_difficulty: str,
                                    ) -> Optional[float]:
        problem_difficulty = problem_difficulty.lower()


        points = self.get_points_based_on_previous_solution_state(user_id, question_id, problem_difficulty)
    
        # update user score and add them to solvers list in db
        try:
            self.firestore_client.add_or_update_user_score(user_id=user_id, score=points)
            self.firestore_client.add_or_update_question(question_id, question_title, datetime.now(), user_id)
        except Exception as e:
            raise e

        return points
    
    def process_points_for_attempt(self,
                                   user_id: str,
                                   problem_difficulty: str,
                                   ) -> Optional[float]:
        problem_difficulty = problem_difficulty.lower()
        """
            This function update user points for attempting and add them to cached list of attempters
            NOTE: this function must be used after checking if the user already attempted or submitted to this question before
        """
        try:
            attempted_difficulty_map = self.redis_client.get_decoded_dict(REDIS_ATTEMPTED_KEY)
            self.add_user_id_to_cached_attempters_list(user_id, problem_difficulty, attempted_difficulty_map)
            self.firestore_client.add_or_update_user_score(user_id, ATTEMPT_PT)
        except Exception as e:
            print(f"Error processing points for attempt: {e}")
            return None

        return ATTEMPT_PT
        
    def get_default_point_type(self, problem_difficulty: str) ->  int:
        if problem_difficulty == "easy":
            return EASY_PT
        
        if problem_difficulty == "medium":
            return MEDIUM_PT

        raise Exception("Unknown problem_difficulty when giving points!")
        
    
    def get_points_based_on_previous_solution_state(self, 
                                                    user_id: str, 
                                                    question_id: str, 
                                                    problem_difficulty: str,
                                                    ) -> float:
        '''Function for determing what points to give a user based on their previous submission state
            and if this is the first time submitting, add their user id to cached list of solvers

        State machine for submisson state
        Case 1: No attempts or solutions --> solution - User gets default points
        Case 2: Solution --> solution - User gets no points
        Case 3: Attempt --> Soluton - User gets an additional half point
        '''
        points = self.get_default_point_type(problem_difficulty) #case 1

        solved_difficulty_map = self.get_submission_or_attempt_cached_dict(REDIS_SOLVED_KEY)
        has_solved = self.user_has_solved_problem_before(user_id, problem_difficulty, solved_difficulty_map)
        if has_solved: #case 2
            print(f"{user_id} has already solved problem before {question_id}, no points given")
            return 0.0 # no points given

        attempted_difficulty_map = self.get_submission_or_attempt_cached_dict(REDIS_ATTEMPTED_KEY)
        has_attempted = self.user_has_attempted_problem_before(user_id, problem_difficulty, attempted_difficulty_map)
        if has_attempted: #case 3
            print(f"{user_id} has already attempted problem {question_id}. But now, they're submitting their solution instead!")
            points = points / 2 #half points

        # user just solved a problem, add them to cached list of solvers
        self.add_user_id_to_cached_solvers_list(user_id, problem_difficulty, solved_difficulty_map)

        return points

    
    def user_has_attempted_problem_before(self, 
                                          user_id: str, 
                                          problem_difficulty: str, 
                                          attempted_difficulty_map: dict[str, List[str]],
                                          ) -> bool:
        if attempted_difficulty_map and problem_difficulty in attempted_difficulty_map and user_id in attempted_difficulty_map[problem_difficulty]:
            return True
        return False
    
    def user_has_solved_problem_before(self, 
                                       user_id: str, 
                                       problem_difficulty: str, 
                                       solved_difficulty_map: dict[str, List[str]],
                                       ) -> bool:
        if solved_difficulty_map and problem_difficulty in solved_difficulty_map and user_id in solved_difficulty_map[problem_difficulty]:
            return True
        return False
    
    def get_submission_or_attempt_cached_dict(self, submission_or_attempt_key: str) -> Dict:
        try:
            return self.redis_client.get_decoded_dict(submission_or_attempt_key)
        except:
            raise Exception("Invalid key: submission_or_attempt_key has to be either REDIS_SOLVED_KEY or REDIS_ATTEMPTED_KEY constant")
        
    
    def add_user_id_to_cached_solvers_list(self, user_id: str, problem_difficulty: str, solved_difficulty_map: Dict):
        users_list = solved_difficulty_map.get(problem_difficulty, [])
        users_list.append(user_id)
        solved_difficulty_map[problem_difficulty] = users_list
        try:
            self.redis_client.set_dict(REDIS_SOLVED_KEY, 
                                    solved_difficulty_map, 
                                    get_ttl_for_next_monday_9am())
        except Exception as e:
            raise Exception(f"There was an issue updating the cache for user: {user_id} for a {problem_difficulty} question. Error message: {e}")

        
    def add_user_id_to_cached_attempters_list(self, user_id: str, problem_difficulty: str, attempted_difficulty_map: Dict):
        users_list = attempted_difficulty_map.get(problem_difficulty, [])
        users_list.append(user_id)
        attempted_difficulty_map[problem_difficulty] = users_list
        try:
            self.redis_client.set_dict(REDIS_ATTEMPTED_KEY, 
                                    attempted_difficulty_map, 
                                    get_ttl_for_next_monday_9am())
        except Exception as e:
            raise Exception(f"There was an issue updating the cache for user: {user_id} for a {problem_difficulty} question. Error message: {e}")

        
  
        


        