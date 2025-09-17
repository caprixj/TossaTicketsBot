from dataclasses import dataclass


@dataclass
class MaterialOrderCostDetailsDTO:
    rate_price: float
    offered_price: float
    rate_cost: int
    single_tax: int
    msend_tax: int
    total_cost: int
