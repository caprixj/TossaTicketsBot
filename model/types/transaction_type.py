from enum import Enum


class TransactionType(str, Enum):
    unknown = 'unknown'
    creator = 'creator'
    tpay = 'tpay'
    tpay_fee = 'tpay_fee'
    award = 'award'
    salary = 'salary'
