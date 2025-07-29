from datetime import datetime

from resources.glob import DATETIME_FORMAT


class Job:
    def __init__(self,
                 position: str = None,
                 name: str = None,
                 salary: int = 0):
        self.position = position  # EmployeePosition
        self.name = name
        self.salary = salary


class SalaryPayout:
    def __init__(self,
                 salary_payout_id: int = 0,
                 plan_date: str = None,
                 fact_date: str = None,
                 paid_out: bool = False):
        self.salary_payout_id = salary_payout_id
        self.plan_date = datetime.strptime(plan_date, DATETIME_FORMAT)
        self.fact_date = datetime.strptime(fact_date, DATETIME_FORMAT) \
            if fact_date is not None else None
        self.paid_out = paid_out


class Employee:
    def __init__(self,
                 user_id: int = 0,
                 position: str = None,
                 salary: int = 0,
                 hired_date: str = None):
        self.user_id = user_id
        self.position = position
        self.salary = salary
        self.hired_date = datetime.strptime(hired_date, DATETIME_FORMAT) \
            if hired_date is not None else None
