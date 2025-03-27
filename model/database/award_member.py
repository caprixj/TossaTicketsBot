from resources.funcs import funcs


class AwardMemberJunction:
    def __init__(self, award_id: str, owner_id: int):
        self.award_id = award_id
        self.owner_id = owner_id
        self.issue_date = funcs.get_current_datetime()
