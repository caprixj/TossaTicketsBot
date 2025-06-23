from enum import Enum


class TransactionResultErrors(str, Enum):
    INSUFFICIENT_FUNDS = '❌ rejected! insufficient funds'
    TPAY_UNAVAILABLE = '❌ rejected! daily transaction limit reached'
