class TpayCallbackData:
    def __init__(self, operation_id: int, sender_id: int):
        self.operation_id = operation_id
        self.sender_id = sender_id
