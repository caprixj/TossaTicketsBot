from enum import Enum


class TicketTransactionType(str, Enum):
    unknown = 'unknown'
    creator = 'creator'
    tpay = 'tpay'
    tpay_fee = 'tpay_fee'
    award = 'award'
    salary = 'salary'


class MaterialTransactionType(str, Enum):
    unknown = 'unknown'
    tbox = 'tbox'
    bank = 'bank'
    market = 'market'
