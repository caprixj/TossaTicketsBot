from datetime import datetime

from resources.const.glob import DATETIME_FORMAT


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
