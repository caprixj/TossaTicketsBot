from dataclasses import dataclass
from typing import List

from model.database.addt_transaction import AddtTransaction
from model.database.delt_transaction import DeltTransaction
from model.database.tpay_transaction import TpayTransaction
from model.database.member import Member


@dataclass
class MytpayResult:
    user_id: int
    tpays: List[TpayTransaction]
    addts: List[AddtTransaction]
    delts: List[DeltTransaction]
    unique_tpay_members: List[Member]

    def empty(self) -> bool:
        return not self.tpays and not self.addts and not self.delts
