from dataclasses import dataclass


@dataclass
class CustomCallbackData:
    callback_name: str
    sender_id: int
    operation_id: int = -1

    def tostr(self):
        return f'{self.callback_name}\t{self.sender_id}\t{self.operation_id}'


async def get_callback_data(data: str) -> CustomCallbackData:
    s = data.split('\t')
    return CustomCallbackData(
        callback_name=s[0],
        sender_id=int(s[1]),
        operation_id=int(s[2])
    )
