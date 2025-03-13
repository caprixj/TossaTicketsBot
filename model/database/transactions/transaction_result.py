from model.database.transactions.tr_error_messages import TransactionResultErrorMessages


class TransactionResult:
    def __init__(self,
                 error_message: TransactionResultErrorMessages = None,
                 valid: bool = False):
        self.error_message = error_message
        self.valid = valid
