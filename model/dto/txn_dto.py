from dataclasses import dataclass

from model.types.enums import TransactionResultErrors


@dataclass
class TransactionResultDTO:
    message: TransactionResultErrors = None
    valid: bool = False
