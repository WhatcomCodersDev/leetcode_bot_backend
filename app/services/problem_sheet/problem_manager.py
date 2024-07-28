import pandas as pd
from datetime import datetime

from constants import PROBLEM_SHEET_PATH
from app.databases.firestore.leetcode_questions import FirestoreLeetCodeCollectionWrapper
from app.services.problem_sheet.problem import Problem
from app.services.problem_utils import get_problem_data_from_spreadsheet, x_to_bool, get_ttl_for_next_monday_9am

class ProblemManager:
    def __init__(self, 
                 firestore_leetcode_collection_wrapper: FirestoreLeetCodeCollectionWrapper,
                 ):
        self.leetcode_collection_wrapper = firestore_leetcode_collection_wrapper
        problem_sheet = self._load_problem_sheet()
        self.easy_problems, self.medium_problems, self.hard_problems = self._split_sheet_by_difficulty(problem_sheet)

    def _load_problem_sheet(self) -> pd.DataFrame:
        converters_dict = {col: x_to_bool for col in ['B75', 'B50', 'NC.io', 'G75', 'LC', 'SP']}
        df = pd.read_csv(PROBLEM_SHEET_PATH, converters=converters_dict)
        return df

    def _split_sheet_by_difficulty(self, df: pd.DataFrame):
        df_easy = df[df['PROBLEM_DIFFICULTY'] == 'Easy']
        df_medium = df[df['PROBLEM_DIFFICULTY'] == 'Medium']
        df_hard = df[df['PROBLEM_DIFFICULTY'] == 'Hard']
        return df_easy, df_medium, df_hard
    
    def select_problem_at_random(self, problem_difficulty: str) -> Problem:
        problem_difficulty_lower = problem_difficulty.lower()
        problems = None

        if problem_difficulty_lower == 'easy':
            problems = self.easy_problems
        elif problem_difficulty_lower == 'medium':
            problems = self.medium_problems
        elif problem_difficulty_lower == 'hard':
            problems = self.hard_problems
        else:
            raise ValueError(f"Invalid problem difficulty: {problem_difficulty_lower}")
        
        problem_series = problems.sample()
        problem_dict = problem_series.to_dict(orient='records')[0]
        print(f'From problem_manager.py: \n {problem_dict}')
        
        return Problem (
            id=int(problem_dict['ID']), 
            name=problem_dict['PROBLEM'],
            link=problem_dict['URL'], 
            category=problem_dict['CATEGORY'], 
            problem_difficulty=problem_dict['PROBLEM_DIFFICULTY'].lower(), 
            tag=problem_dict['TAG'], 
            isInBlind75=problem_dict['B75'],
            isInBlind50=problem_dict['B50'],
            isInNeetcode=problem_dict['NC.io'],
            isInGrind75=problem_dict['G75'],
            isInSeanPrasadList=problem_dict['SP'],
        )
    
    def get_problem_by_id(self, problem_id: int) -> Problem:
        problem_data = get_problem_data_from_spreadsheet(problem_id)
        return problem_data

    
    def get_problem(self, problem_difficulty: str) -> Problem:
        '''Get a problem at random from spreadsheet based on problem_difficulty
        '''
        problem_data = self.select_problem_at_random(problem_difficulty)
        self.update_db(problem_data)
    
        return problem_data
    
    def get_all_problems(self):
        problems = []

        self.easy_problems['CATEGORY'] = self.easy_problems['CATEGORY'].fillna('')#temp
        self.medium_problems['CATEGORY'] = self.medium_problems['CATEGORY'].fillna('')#temp
        self.hard_problems['CATEGORY'] = self.hard_problems['CATEGORY'].fillna('')#temp

        for _, row in self.easy_problems.iterrows():
            problem = Problem(
                id=row['ID'], 
                name=row['PROBLEM'],
                link=row['URL'], 
                category=row['CATEGORY'],
                problem_difficulty=row['PROBLEM_DIFFICULTY'].lower(), 
                tag=row['TAG'], 
                isInBlind75=row['B75'],
                isInBlind50=row['B50'],
                isInNeetcode=row['NC.io'],
                isInGrind75=row['G75'],
                isInSeanPrasadList=row['SP'],
                )
            problems.append(problem)
        
        for _, row in self.medium_problems.iterrows():
            problem = Problem(
                id=row['ID'], 
                name=row['PROBLEM'],
                link=row['URL'],
                category=row['CATEGORY'], 
                problem_difficulty=row['PROBLEM_DIFFICULTY'].lower(), 
                tag=row['TAG'], 
                isInBlind75=row['B75'],
                isInBlind50=row['B50'],
                isInNeetcode=row['NC.io'],
                isInGrind75=row['G75'],
                isInSeanPrasadList=row['SP'],
            )
            problems.append(problem)
        
        for _, row in self.hard_problems.iterrows():
            problem = Problem(
                id=row['ID'], 
                name=row['PROBLEM'],
                link=row['URL'], 
                category=row['CATEGORY'], 
                problem_difficulty=row['PROBLEM_DIFFICULTY'].lower(), 
                tag=row['TAG'], 
                isInBlind75=row['B75'],
                isInBlind50=row['B50'],
                isInNeetcode=row['NC.io'],
                isInGrind75=row['G75'],
                isInSeanPrasadList=row['SP'],
            )
            problems.append(problem)
        return problems
    
        
    def update_db(self, problem: Problem):
        self.leetcode_collection_wrapper.update_question_document(
            question_id=str(problem.id), 
            question_title=problem.name,
            last_asked_timestamp=datetime.now()
            )

    