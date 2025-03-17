from enum import Enum


class TransactionType(str, Enum):
    unknown = 'unknown'
    tpay = 'tpay'
    tpay_fee = 'tpay_fee'
