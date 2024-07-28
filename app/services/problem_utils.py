import pandas as pd
from datetime import datetime
from datetime import timedelta
from app.services.problem_sheet.problem import Problem
from constants import PROBLEM_SHEET_PATH 

def get_problem_data_from_spreadsheet(id: int) -> Problem:
    # print(id, type(id))
    converters_dict = {col: x_to_bool for col in ['B75', 'B50', 'NC.io', 'G75', 'LC', 'SP']}

    df = pd.read_csv(PROBLEM_SHEET_PATH, converters=converters_dict)
    # print(list(df))

    df_problem = df[df['ID'] == id]
    df_problem = df_problem.dropna(subset=['CATEGORY'])
    problem_dict = df_problem.to_dict(orient='records')[0]
        
    return Problem(id=int(problem_dict['ID']), 
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
                            # notes=problem_dict['NOTES']
                            )

def x_to_bool(value):
    if value == 'x':  # Adjust this if your true indicator is different
        return True
    elif pd.isnull(value) or value == '':  # Assuming empty cells or a specific character indicate False
        return False
    else:
        return False  # You can adjust this else-case based on your data specifics
    
def get_ttl_for_next_monday_9am() -> int:
    now = datetime.now()
    # Find how many days to add to get to the next Monday (1 = Monday, 0 = Sunday)
    days_until_monday = (7 - now.weekday()) % 7
    if days_until_monday == 0 and now.hour >= 9:
        # If it's Monday but past 9 AM, wait until next Monday
        days_until_monday = 7
    # Calculate next Monday at 9 AM
    next_monday_9am = now.replace(hour=9, minute=0, second=0, microsecond=0) + timedelta(days=days_until_monday)
    # Calculate TTL in seconds
    ttl_seconds = (next_monday_9am - now).total_seconds()
    print(f"Util.py: seconds left till next monday {int(ttl_seconds)}")
    return int(ttl_seconds)
