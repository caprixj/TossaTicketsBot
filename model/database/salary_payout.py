from datetime import datetime

from resources.const.glob import DATETIME_FORMAT


class SalaryPayout:
    def __init__(self,
                 salary_payout_id: int = 0,
                 date: str = None,
                 paid_out: bool = False):
        self.salary_payout_id = salary_payout_id
        self.date = datetime.strptime(date, DATETIME_FORMAT)
        self.paid_out = paid_out
