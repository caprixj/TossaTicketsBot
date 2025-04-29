from dataclasses import dataclass

from model.types.transaction_result_errors import TransactionResultErrors


@dataclass
class TransactionResultDTO:
    message: TransactionResultErrors = None
    valid: bool = False
