from enum import Enum


# class TicketTransactionType(str, Enum):
#     unknown = 'unknown'
#     creator = 'creator'
#     unreg = 'unreg'
#     tpay = 'tpay'
#     tpay_tax = 'tpay_tax'
#     nbt = 'nbt'
#     nbt_tax = 'nbt_tax'
#     market = 'market'
#     market_tax = 'market_tax'
#     market_fee = 'market_fee'
#     award = 'award'
#     salary = 'salary'
#
#
# class MaterialTransactionType(str, Enum):
#     unknown = 'unknown'
#     tbox = 'tbox'
#     nbt = 'nbt'
#     market = 'market'


class TicketTransactionType(str, Enum):
    UNKNOWN = 'unknown'
    CREATOR = 'creator'
    UNREG = 'unreg'
    TPAY = 'tpay'
    MSELL = 'msell'
    MSEND = 'msend'
    AWARD = 'award'
    SALARY = 'salary'


class MaterialTransactionType(str, Enum):
    UNKNOWN = 'unknown'
    TBOX = 'tbox'
    MSELL = 'msell'
    MSEND = 'msend'
    MSEND_MANUAL = 'msend_manual'


class TaxTransactionType(str, Enum):
    UNKNOWN = 'unknown'
    SINGLE_TPAY = 'single_tpay'
    SINGLE_MSELL = 'single_msell'
