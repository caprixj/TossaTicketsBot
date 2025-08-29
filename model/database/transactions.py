from model.types import TicketTxnType
from model.types.profit_type import ProfitType
from model.types.transaction_types import MaterialTxnType, TaxType, TaxParentType
from resources import funcs


class TicketTransaction:
    def __init__(self,
                 ticket_txn_id: int = 0,
                 sender_id: int = -1,
                 receiver_id: int = -1,
                 transfer: int = 0,
                 txn_type: TicketTxnType = TicketTxnType.UNKNOWN,
                 time: str = None,
                 description: str = None):
        self.ticket_txn_id = ticket_txn_id
        self.sender_id = sender_id
        self.receiver_id = receiver_id
        self.transfer = transfer
        self.type = txn_type
        self.time = funcs.to_utc(time)
        self.description = description


class TaxTransaction:
    def __init__(self,
                 tax_txn_id: int = 0,
                 parent_id: int = 0,
                 user_id: int = 0,
                 amount: int = 0,
                 tax_type: TaxType = TaxType.UNKNOWN,
                 parent_type: TaxParentType = TaxParentType.UNKNOWN,
                 time: str = None):
        self.tax_txn_id = tax_txn_id
        self.parent_id = parent_id
        self.user_id = user_id
        self.amount = amount
        self.tax_type = tax_type
        self.parent_type = parent_type
        self.time = funcs.to_utc(time)


class MaterialTransaction:
    def __init__(self,
                 mat_txn_id: int = 0,
                 sender_id: int = -1,
                 receiver_id: int = -1,
                 type_: MaterialTxnType = MaterialTxnType.UNKNOWN,
                 material_name: str = 0,
                 quantity: int = 0,
                 ticket_txn: int = 0,
                 date: str = None,
                 description: str = None):
        self.mat_txn_id = mat_txn_id
        self.sender_id = sender_id
        self.receiver_id = receiver_id
        self.type_ = type_
        self.material_name = material_name
        self.quantity = quantity
        self.ticket_txn = ticket_txn
        self.date = funcs.to_utc(date)
        self.description = description


class BusinessProfitTransaction:
    def __init__(self,
                 business_profit_id: int = 0,
                 user_id: int = 0,
                 profit_type: ProfitType = ProfitType.UNKNOWN,
                 transfer: int = 0,
                 date: str = None,
                 artifact_id: int = 0):
        self.business_profit_id = business_profit_id
        self.user_id = user_id
        self.profit_type = profit_type
        self.transfer = transfer
        self.date = funcs.to_utc(date)
        self.artifact_id = artifact_id


class BusinessWithdrawTransaction:
    def __init__(self,
                 business_withdraw_id: int = 0,
                 user_id: int = 0,
                 transfer: int = 0,
                 date: str = None):
        self.business_withdraw_id = business_withdraw_id
        self.user_id = user_id
        self.transfer = transfer
        self.date = funcs.to_utc(date)
