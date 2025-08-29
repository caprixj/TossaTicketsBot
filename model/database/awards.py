from resources import funcs


class Award:
    def __init__(self,
                 award_id: str = None,
                 name: str = None,
                 description: str = None,
                 payment: int = 0):
        self.award_id = award_id  # SID
        self.name = name  # Text64
        self.description = description  # Text512
        self.payment = payment


class AwardMember:
    def __init__(self, award_id: str, owner_id: int):
        self.award_id = award_id
        self.owner_id = owner_id
        self.issue_date = funcs.utcnow_str()
