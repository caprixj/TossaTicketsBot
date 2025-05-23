class Member:
    def __init__(self,
                 user_id: int = 0,
                 username: str = None,
                 first_name: str = None,
                 last_name: str = None,
                 tickets: float = 0.0,
                 tpay_available: int = 3,
                 business_account: float = 0.0,
                 tbox_available: int = 1,
                 anchor: int = 0):
        self.user_id = user_id
        self.username = username
        self.first_name = first_name
        self.last_name = last_name
        self.tickets = tickets
        self.tpay_available = tpay_available
        self.business_account = business_account
        self.tbox_available = tbox_available
        self.anchor = anchor  # native chat id
