from enum import Enum


class TransactionResultErrorMessages(str, Enum):
    insufficient_funds = '❌ відхилено! недостатньо коштів'
    tpay_unavailable = '❌ відхилено! вичерпано добовий ліміт на транзакції'
    receiver_sanctioned = '❌ відхилено! на отримувача накладені санкції'
