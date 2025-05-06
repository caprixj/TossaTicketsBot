from resources.funcs import funcs


class Award:
    def __init__(self,
                 award_id: str = None,
                 name: str = None,
                 description: str = None,
                 payment: float = 0.0):
        self.award_id = award_id  # SID
        self.name = name  # Text64
        self.description = description  # Text512
        self.payment = payment


class AwardMemberJunction:
    def __init__(self, award_id: str, owner_id: int):
        self.award_id = award_id
        self.owner_id = owner_id
        self.issue_date = funcs.get_current_datetime()
