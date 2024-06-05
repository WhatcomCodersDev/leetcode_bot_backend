import pandas as pd
from datetime import datetime

from constants import PROBLEM_SHEET_PATH, REDIS_EASY_PROBLEM_ID_KEY, REDIS_MEDIUM_PROBLEM_ID_KEY
from app.services.problem import Problem
from util import get_problem_data_from_spreadsheet, x_to_bool, get_ttl_for_next_monday_9am



class ProblemManager:
    def __init__(self, db, redis_client):
        self.db = db
        self.redis_client = redis_client
        problem_sheet = self._load_problem_sheet()
        self.easy_problems, self.medium_problems, self.hard_problems = self._split_sheet_by_difficulty(problem_sheet)

    def _load_problem_sheet(self) -> pd.DataFrame:
        converters_dict = {col: x_to_bool for col in ['B75', 'B50', 'NC.io', 'G75', 'LC', 'SP']}

        df = pd.read_csv(PROBLEM_SHEET_PATH, converters=converters_dict)
        return df

    def _split_sheet_by_difficulty(self, df: pd.DataFrame):
        df_easy = df[df['LEVEL'] == 'Easy']
        df_medium = df[df['LEVEL'] == 'Medium']
        df_hard = df[df['LEVEL'] == 'Hard']
        return df_easy, df_medium, df_hard
    
    def select_problem_at_random(self, difficulty: str) -> Problem:
        difficulty_lower = difficulty.lower()
        problems = None

        if difficulty_lower == 'easy':
            problems = self.easy_problems
        elif difficulty_lower == 'medium':
            problems = self.medium_problems
        elif difficulty_lower == 'hard':
            problems = self.hard_problems
        else:
            raise ValueError(f"Invalid difficulty: {difficulty_lower}")
        
        problem_series = problems.sample()
        problem_dict = problem_series.to_dict(orient='records')[0]
        print(f'From problem_manager.py: \n {problem_dict}')
        
        return Problem(id=int(problem_dict['ID']), 
                            name=problem_dict['PROBLEM'],
                            link=problem_dict['URL'], 
                            type=problem_dict['TYPE'], 
                            difficulty=problem_dict['LEVEL'].lower(), 
                            tag=problem_dict['TAG'], 
                            isInBlind75=problem_dict['B75'],
                            isInBlind50=problem_dict['B50'],
                            isInNeetcode=problem_dict['NC.io'],
                            isInGrind75=problem_dict['G75'],
                            isInSeanPrasadList=problem_dict['SP'],
                            # notes=problem_dict['NOTES']
                            )
    
    def get_problem_by_id(self, problem_id: int) -> Problem:
        problem_data = get_problem_data_from_spreadsheet(problem_id)
        return problem_data

    
    def get_problem(self, difficulty: str) -> Problem:
        '''Get a problem at random from spreadsheet based on difficulty

        If a problem is currently active, we will fetch the problem id from redis.
        Then we get the problem data from the spreadsheet directly and pass this information

        If no problem is active, this means we need to send a new one. We will randomly
        fetch one from the spreadsheet. And update the cache and database
        '''

        problem_data = None

        #TODO: make a util function to make this easier and reusable or make a hashmap as a constant
        if difficulty.lower() == 'easy':
            redis_key = REDIS_EASY_PROBLEM_ID_KEY
        elif difficulty.lower() == 'medium':
            redis_key = REDIS_MEDIUM_PROBLEM_ID_KEY
        else:
            raise Exception(f"Error: no redis key exist for {difficulty}, please make one and retry")


        if not self.redis_client.get_value(redis_key): 
            #TODO: make keys not confusing, we have key which is problem difficulty to user_ids and problem difficulty to problem_id
            problem_data = self.select_problem_at_random(difficulty)
            self.update_db(problem_data)
            self.redis_client.set_value(redis_key, problem_data.id, get_ttl_for_next_monday_9am())
        else:
            problem_id = self.redis_client.get_decoded_value(redis_key)
            if problem_id:
                problem_data = get_problem_data_from_spreadsheet(problem_id)

        return problem_data
    
    def get_all_problems(self):
        problems = []

        self.easy_problems['TYPE'] = self.easy_problems['TYPE'].fillna('')#temp
        self.medium_problems['TYPE'] = self.medium_problems['TYPE'].fillna('')#temp
        self.hard_problems['TYPE'] = self.hard_problems['TYPE'].fillna('')#temp

        for index, row in self.easy_problems.iterrows():
            # row['NOTES'] = ''#temp
            # row['TYPE'] = ''
            problem = Problem(id=row['ID'], 
                            name=row['PROBLEM'],
                            link=row['URL'], 
                            type=row['TYPE'],
                            difficulty=row['LEVEL'].lower(), 
                            tag=row['TAG'], 
                            isInBlind75=row['B75'],
                            isInBlind50=row['B50'],
                            isInNeetcode=row['NC.io'],
                            isInGrind75=row['G75'],
                            isInSeanPrasadList=row['SP'],
                            # notes=row['NOTES']
                            )
            problems.append(problem)
        
        for index, row in self.medium_problems.iterrows():
            # row['NOTES'] = ''
            # row['TYPE'] = ''
            problem = Problem(id=row['ID'], 
                            name=row['PROBLEM'],
                            link=row['URL'],
                            type=row['TYPE'], 
                            difficulty=row['LEVEL'].lower(), 
                            tag=row['TAG'], 
                            isInBlind75=row['B75'],
                            isInBlind50=row['B50'],
                            isInNeetcode=row['NC.io'],
                            isInGrind75=row['G75'],
                            isInSeanPrasadList=row['SP'],
                            # notes=row['NOTES']
                            )
            problems.append(problem)
        
        for index, row in self.hard_problems.iterrows():
            # row['NOTES'] = ''
            # row['TYPE'] = ''
            problem = Problem(id=row['ID'], 
                            name=row['PROBLEM'],
                            link=row['URL'], 
                            type=row['TYPE'], 
                            difficulty=row['LEVEL'].lower(), 
                            tag=row['TAG'], 
                            isInBlind75=row['B75'],
                            isInBlind50=row['B50'],
                            isInNeetcode=row['NC.io'],
                            isInGrind75=row['G75'],
                            isInSeanPrasadList=row['SP'],
                            # notes=row['NOTES']
                            )
            problems.append(problem)
        print("Problems from get_all_problems", problems)
        return problems
    
        
    def update_db(self, problem: Problem):
        self.db.update_question_document(question_id=str(problem.id), 
                                        question_title=problem.name,
                                        last_asked_timestamp=datetime.now())

    