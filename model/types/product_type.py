from enum import Enum


class ProductType(str, Enum):
    unknown = 'unknown'
    gemstone = 'gemstone'
    craft = 'craft'
    service = 'service'
