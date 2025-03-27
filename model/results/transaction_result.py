from model.types.transaction_result_errors import TransactionResultErrors


class TransactionResult:
    def __init__(self,
                 message: TransactionResultErrors = None,
                 valid: bool = False):
        self.message = message
        self.valid = valid
