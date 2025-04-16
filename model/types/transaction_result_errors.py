from enum import Enum


class TransactionResultErrors(str, Enum):
    insufficient_funds = '❌ rejected! insufficient funds'
    tpay_unavailable = '❌ rejected! daily transaction limit reached'
