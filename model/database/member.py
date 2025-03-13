class Member:
    def __init__(self,
                 user_id: int = 0,
                 username: str = None,
                 first_name: str = None,
                 last_name: str = None,
                 tickets_count: int = 0,
                 tpay_available: int = 3):
        self.user_id = user_id
        self.username = username
        self.first_name = first_name
        self.last_name = last_name
        self.tickets_count = tickets_count
        self.tpay_available = tpay_available
