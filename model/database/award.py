from model.ticketonomics_types import SID, Text64, Text512


class Award:
    def __init__(self,
                 award_id: str = 0,
                 name: str = None,
                 description: str = None,
                 payment: float = None
                 ):
        self.award_id = SID(award_id).cast()
        self.name = Text64(name).cast()
        self.description = Text512(description).cast()
        self.payment = payment
