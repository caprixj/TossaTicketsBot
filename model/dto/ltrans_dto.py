from dataclasses import dataclass

from model.database.member import Member
from model.database.transactions import TicketTransaction, TaxTransaction


@dataclass
class TxnDTO:
    user_id: int
    tpays: dict[TicketTransaction, int]
    msends: dict[TicketTransaction, int]
    addts: list[TicketTransaction]
    delts: list[TicketTransaction]
    msells: list[TicketTransaction]
    salaries: list[TicketTransaction]
    awards: list[TicketTransaction]
    unknowns: list[TicketTransaction]
    taxes: list[TaxTransaction]
    unique_transfer_members: list[Member]

    def empty(self) -> bool:
        return not any((self.tpays, self.msends, self.addts, self.delts, self.msells,
                        self.salaries, self.awards, self.unknowns, self.taxes))
