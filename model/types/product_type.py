from enum import Enum


class ProductType(str, Enum):
    unclassified = 'unclassified'
    prime = 'prime'
    craft = 'craft'
    service = 'service'
