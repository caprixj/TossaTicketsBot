from datetime import datetime

from resources.const.glob import DATETIME_FORMAT


class Employee:
    def __init__(self,
                 user_id: int = 0,
                 position: str = None,
                 salary: float = 0,
                 hired_date: str = None):
        self.user_id = user_id
        self.position = position
        self.salary = salary
        self.hired_date = datetime.strptime(hired_date, DATETIME_FORMAT) \
            if hired_date is not None else None
