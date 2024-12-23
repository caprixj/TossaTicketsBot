from datetime import datetime


class AddtTransaction:
    def __init__(self,
                 addt_id: int = 0,
                 user_id: int = 0,
                 tickets_count: int = 0,
                 transaction_time: str = None,
                 description: str = None):
        self.addt_id = addt_id
        self.user_id = user_id
        self.tickets_count = tickets_count
        self.transaction_time = datetime.strptime(transaction_time, '%Y-%m-%d %H:%M:%S')
        self.description = description
