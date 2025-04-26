from dataclasses import dataclass
from typing import List

from model.database import TpayTransaction, AddtTransaction, DeltTransaction, Member


@dataclass
class LTransDTO:
    user_id: int
    tpays: List[TpayTransaction]
    addts: List[AddtTransaction]
    delts: List[DeltTransaction]
    unique_tpay_members: List[Member]

    def empty(self) -> bool:
        return not self.tpays and not self.addts and not self.delts
