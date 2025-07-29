from enum import Enum


class TicketTxnType(str, Enum):
    UNKNOWN = 'unknown'
    CREATOR = 'creator'
    ADMIN = 'admin'
    UNREG = 'unreg'
    TPAY = 'tpay'
    MSELL = 'msell'
    MSEND = 'msend'
    AWARD = 'award'
    SALARY = 'salary'


class MaterialTxnType(str, Enum):
    UNKNOWN = 'unknown'
    TBOX = 'tbox'
    MSELL = 'msell'
    MSEND = 'msend'


class TaxType(str, Enum):
    UNKNOWN = 'unknown'
    SINGLE = 'single'
    MSELL = 'msell'


class TaxParentType(str, Enum):
    UNKNOWN = 'unknown'
    TICKET = 'ticket'
    MATERIAL = 'material'
