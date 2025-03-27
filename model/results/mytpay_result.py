from typing import List

from model.database.addt_transaction import AddtTransaction
from model.database.delt_transaction import DeltTransaction
from model.database.tpay_transaction import TpayTransaction
from model.database.member import Member


class MytpayResult:
    def __init__(self, user_id: int, tpays: List[TpayTransaction], addts: List[AddtTransaction],
                 delts: List[DeltTransaction], unique_tpay_members: List[Member]):
        self.user_id = user_id
        self.tpays = tpays
        self.addts = addts
        self.delts = delts
        self.unique_tpay_members = unique_tpay_members
