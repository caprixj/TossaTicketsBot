from datetime import datetime

from model.types import ProductType
from resources.const.glob import DATETIME_FORMAT


class Price:
    def __init__(self,
                 product_name: str = None,
                 product_type: ProductType = ProductType.unknown,
                 price: float = 0.0):
        self.product_name = product_name
        self.product_type = product_type
        self.price = price


class RateReset:
    def __init__(self,
                 rate_history_id: int = 0,
                 inflation: float = 0.0,
                 fluctuation: float = 0.0,
                 plan_date: str = None,
                 fact_date: str = None):
        self.rate_history_id = rate_history_id
        self.inflation = inflation
        self.fluctuation = fluctuation
        self.plan_date = datetime.strptime(plan_date, DATETIME_FORMAT)
        self.fact_date = datetime.strptime(fact_date, DATETIME_FORMAT)


class PriceHistory:
    def __init__(self,
                 price_history_id: int = 0,
                 product_name: str = None,
                 product_type: ProductType = ProductType.unknown,
                 price: float = 0.0,
                 reset_date: str = None):
        self.price_history_id = price_history_id
        self.product_name = product_name
        self.product_type = product_type
        self.price = price
        self.reset_date = datetime.strptime(reset_date, DATETIME_FORMAT)
