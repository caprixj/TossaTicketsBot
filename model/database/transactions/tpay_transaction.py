from datetime import datetime


class TpayTransaction:
    def __init__(self,
                 tpay_id: int = 0,
                 sender_id: int = 0,
                 receiver_id: int = 0,
                 transfer_amount: int = 0,
                 fee_amount: int = 0,
                 transaction_time: str = None,
                 description: str = None):
        self.tpay_id = tpay_id
        self.sender_id = sender_id
        self.receiver_id = receiver_id
        self.transfer_amount = transfer_amount
        self.fee_amount = fee_amount
        self.transaction_time = datetime.strptime(transaction_time, '%Y-%m-%d %H:%M:%S')
        self.description = description
