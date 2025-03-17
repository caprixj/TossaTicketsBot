from datetime import datetime

from model.database.transactions.transaction_type import TransactionType


class AddtTransaction:
    def __init__(self,
                 addt_id: int = 0,
                 user_id: int = 0,
                 tickets: int = 0,
                 time: str = None,
                 description: str = None,
                 type_: TransactionType = TransactionType.unknown):
        self.addt_id = addt_id
        self.user_id = user_id
        self.tickets = tickets
        self.time = datetime.strptime(time, '%Y-%m-%d %H:%M:%S')
        self.description = description
        self.type_ = type_
