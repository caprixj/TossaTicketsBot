class Award:
    def __init__(self,
                 award_id: str = 0,
                 name: str = None,
                 description: str = None,
                 payment: float = None):
        self.award_id = award_id  # SID
        self.name = name  # Text64
        self.description = description  # Text512
        self.payment = payment
