from datetime import datetime

from resources.const.glob import DATETIME_FORMAT


class PriceReset:
    def __init__(self,
                 price_history_id: int = 0,
                 inflation: float = 0,
                 fluctuation: float = 0,
                 plan_date: str = None,
                 fact_date: str = None):
        self.price_history_id = price_history_id
        self.inflation = inflation
        self.fluctuation = fluctuation
        self.plan_date = datetime.strptime(plan_date, DATETIME_FORMAT)
        self.fact_date = datetime.strptime(fact_date, DATETIME_FORMAT)
