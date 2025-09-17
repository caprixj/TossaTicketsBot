from model.types.enums import ProductType
from utils import funcs


class Price:
    def __init__(self,
                 product_name: str = None,
                 product_type: ProductType = ProductType.UNKNOWN,
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
        self.plan_date = funcs.to_utc(plan_date)
        self.fact_date = funcs.to_utc(fact_date)


class PriceHistory:
    def __init__(self,
                 price_history_id: int = 0,
                 product_name: str = None,
                 product_type: ProductType = ProductType.UNKNOWN,
                 price: float = 0.0,
                 reset_date: str = None):
        self.price_history_id = price_history_id
        self.product_name = product_name
        self.product_type = product_type
        self.price = price
        self.reset_date = funcs.to_utc(reset_date)
