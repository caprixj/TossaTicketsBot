from dataclasses import dataclass

from model.database import TicketTransaction, TaxTransaction, Member


@dataclass
class LTransDTO:
    user_id: int
    tpays: dict[TicketTransaction, int]
    addts: list[TicketTransaction]
    delts: list[TicketTransaction]
    msells: list[TicketTransaction]
    salaries: list[TicketTransaction]
    awards: list[TicketTransaction]
    unknowns: list[TicketTransaction]
    taxes: list[TaxTransaction]
    unique_tpay_members: list[Member]

    def empty(self) -> bool:
        return not any((self.tpays, self.addts, self.delts, self.msells,
                        self.salaries, self.awards, self.unknowns, self.taxes))
