from datetime import datetime

from model.types import TransactionType
from resources.const.glob import DATETIME_FORMAT


class AddtTransaction:
    def __init__(self,
                 addt_id: int = 0,
                 user_id: int = 0,
                 tickets: float = 0,
                 time: str = None,
                 description: str = None,
                 type_: TransactionType = TransactionType.unknown):
        self.addt_id = addt_id
        self.user_id = user_id
        self.tickets = tickets
        self.time = datetime.strptime(time, DATETIME_FORMAT)
        self.description = description
        self.type_ = type_


class DeltTransaction:
    def __init__(self,
                 delt_id: int = 0,
                 user_id: int = 0,
                 tickets: float = 0,
                 time: str = None,
                 description: str = None,
                 type_: TransactionType = TransactionType.unknown):
        self.delt_id = delt_id
        self.user_id = user_id
        self.tickets = tickets
        self.time = datetime.strptime(time, DATETIME_FORMAT)
        self.description = description
        self.type_ = type_


class TpayTransaction:
    def __init__(self,
                 tpay_id: int = 0,
                 sender_id: int = 0,
                 receiver_id: int = 0,
                 transfer: float = 0,
                 fee: float = 0,
                 time: str = None,
                 description: str = None):
        self.tpay_id = tpay_id
        self.sender_id = sender_id
        self.receiver_id = receiver_id
        self.transfer = transfer
        self.fee = fee
        self.time = datetime.strptime(time, DATETIME_FORMAT)
        self.description = description
