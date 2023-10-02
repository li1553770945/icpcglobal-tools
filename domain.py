from typing import List


class Person:
    def __init__(self, name: str, english_name: str, email: str):
        self.name = name
        self.english_name = english_name
        self.email = email


class Team:
    def __init__(self,school:str, name: str, english_name: str, team_id, contestants: List[Person], coach: Person):
        self.school = school
        self.name = name
        self.english_name = english_name
        self.contestants = contestants
        self.coach = coach
        self.team_id = team_id
        self.status = None


class School:
    def __init__(self, name: str, english_name: str):
        self.name = name
        self.english_name = english_name
        self.teams = list()
