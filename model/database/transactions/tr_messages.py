from enum import Enum


class TransactionResultMessages(str, Enum):
    insufficient_funds = '❌ відхилено! недостатньо коштів'
    tpay_unavailable = '❌ відхилено! вичерпано добовий ліміт на транзакції'
