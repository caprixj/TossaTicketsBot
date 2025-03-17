from model.database.transactions.tr_messages import TransactionResultMessages


class TransactionResult:
    def __init__(self,
                 message: TransactionResultMessages = None,
                 valid: bool = False):
        self.message = message
        self.valid = valid
