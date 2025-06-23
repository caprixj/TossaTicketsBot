from enum import Enum


class ProductType(str, Enum):
    UNKNOWN = 'unknown'
    GEMSTONE = 'gemstone'
    CRAFT = 'craft'
    SERVICE = 'service'
