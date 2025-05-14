from datetime import datetime

from model.types import TicketTransactionType
from model.types.profit_type import ProfitType
from model.types.transaction_types import MaterialTransactionType
from resources.const.glob import DATETIME_FORMAT


class AddtTransaction:
    def __init__(self,
                 addt_id: int = 0,
                 user_id: int = 0,
                 tickets: float = 0,
                 time: str = None,
                 description: str = None,
                 type_: TicketTransactionType = TicketTransactionType.unknown):
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
                 tickets: float = 0.0,
                 time: str = None,
                 description: str = None,
                 type_: TicketTransactionType = TicketTransactionType.unknown):
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
                 transfer: float = 0.0,
                 fee: float = 0.0,
                 time: str = None,
                 description: str = None):
        self.tpay_id = tpay_id
        self.sender_id = sender_id
        self.receiver_id = receiver_id
        self.transfer = transfer
        self.fee = fee
        self.time = datetime.strptime(time, DATETIME_FORMAT)
        self.description = description


class MaterialTransaction:
    def __init__(self,
                 material_transaction_id: int = 0,
                 sender_id: int = -1,
                 receiver_id: int = -1,
                 type_: MaterialTransactionType = MaterialTransactionType.unknown,
                 material_name: str = 0,
                 quantity: int = 0,
                 transfer: float = 0.0,
                 tax: float = 0.0,
                 date: str = None,
                 description: str = None):
        self.material_transaction_id = material_transaction_id
        self.sender_id = sender_id
        self.receiver_id = receiver_id
        self.type_ = type_
        self.material_name = material_name
        self.quantity = quantity
        self.transfer = transfer
        self.tax = tax
        self.date = datetime.strptime(date, DATETIME_FORMAT)
        self.description = description


class BusinessProfitTransaction:
    def __init__(self,
                 business_profit_id: int = 0,
                 user_id: int = 0,
                 profit_type: ProfitType = ProfitType.unknown,
                 transfer: float = 0,
                 date: str = None,
                 artifact_id: int = 0):
        self.business_profit_id = business_profit_id
        self.user_id = user_id
        self.profit_type = profit_type
        self.transfer = transfer
        self.date = datetime.strptime(date, DATETIME_FORMAT)
        self.artifact_id = artifact_id


class BusinessWithdrawTransaction:
    def __init__(self,
                 business_withdraw_id: int = 0,
                 user_id: int = 0,
                 transfer: float = 0,
                 date: str = None):
        self.business_withdraw_id = business_withdraw_id
        self.user_id = user_id
        self.transfer = transfer
        self.date = datetime.strptime(date, DATETIME_FORMAT)
