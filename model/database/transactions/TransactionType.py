from enum import Enum


class TransactionType(str, Enum):
    unknown = 'unknown'
    creator = 'creator'
    tpay = 'tpay'
    tpay_fee = 'tpay_fee'
    tkick = 'tkick'
    tmute = 'tmute'
    tban = 'tban'
    demute = 'demute'
    deban = 'deban'
