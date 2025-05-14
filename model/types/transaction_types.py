from enum import Enum


class TicketTransactionType(str, Enum):
    unknown = 'unknown'
    creator = 'creator'
    tpay = 'tpay'
    tpay_tax = 'tpay_tax'
    nbt = 'nbt'
    nbt_tax = 'nbt_tax'
    market = 'market'
    market_tax = 'market_tax'
    market_fee = 'market_fee'
    award = 'award'
    salary = 'salary'


class MaterialTransactionType(str, Enum):
    unknown = 'unknown'
    tbox = 'tbox'
    nbt = 'nbt'
    market = 'market'
