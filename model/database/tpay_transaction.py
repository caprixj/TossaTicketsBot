from datetime import datetime


class TpayTransaction:
    def __init__(self,
                 tpay_id: int = 0,
                 sender_id: int = 0,
                 receiver_id: int = 0,
                 transfer: float = 0,
                 fee: float = 0,
                 time: str = None,
                 description: str = None):
        self.tpay_id = tpay_id
        self.sender_id = sender_id
        self.receiver_id = receiver_id
        self.transfer = transfer
        self.fee = fee
        self.time = datetime.strptime(time, '%Y-%m-%d %H:%M:%S')
        self.description = description
