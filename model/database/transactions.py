from datetime import datetime

from model.types import TicketTransactionType
from model.types.profit_type import ProfitType
from model.types.transaction_types import MaterialTransactionType, TaxTransactionType
from resources.const.glob import DATETIME_FORMAT


class TicketTransaction:
    def __init__(self,
                 ticket_txn_id: int = 0,
                 sender_id: int = -1,
                 receiver_id: int = -1,
                 transfer: float = 0.0,
                 type_: TicketTransactionType = TicketTransactionType.UNKNOWN,
                 time: str = None,
                 description: str = None):
        self.ticket_txn_id = ticket_txn_id
        self.sender_id = sender_id
        self.receiver_id = receiver_id
        self.transfer = transfer
        self.type = type_
        self.time = datetime.strptime(time, DATETIME_FORMAT)
        self.description = description


class TaxTransaction:
    def __init__(self,
                 tax_txn_id: int = 0,
                 ticket_txn_id: int = 0,
                 user_id: int = 0,
                 amount: float = 0.0,
                 type_: TaxTransactionType = TaxTransactionType.UNKNOWN,
                 time: str = None):
        self.tax_txn_id = tax_txn_id
        self.ticket_txn_id = ticket_txn_id
        self.user_id = user_id
        self.amount = amount
        self.type = type_
        self.time = datetime.strptime(time, DATETIME_FORMAT)


class MaterialTransaction:
    def __init__(self,
                 material_transaction_id: int = 0,
                 sender_id: int = -1,
                 receiver_id: int = -1,
                 type_: MaterialTransactionType = MaterialTransactionType.UNKNOWN,
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
