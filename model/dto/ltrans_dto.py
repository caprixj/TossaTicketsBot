from dataclasses import dataclass

from model.database import AddtTransaction, DeltTransaction, TpayTransaction, Member


@dataclass
class LTransDTO:
    user_id: int
    tpays: list[TpayTransaction]
    addts: list[AddtTransaction]
    delts: list[DeltTransaction]
    unique_tpay_members: list[Member]

    def empty(self) -> bool:
        return not self.tpays and not self.addts and not self.delts
