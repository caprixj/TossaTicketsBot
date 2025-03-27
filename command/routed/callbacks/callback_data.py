from typing import Optional


class CustomCallbackData:
    def __init__(self, operation_id: int, sender_id: int):
        self.operation_id = operation_id
        self.sender_id = sender_id


def generate_callback_data(name: str, *args) -> Optional[str]:
    data_list = list(args)
    callback_str = name

    for data in data_list:
        callback_str += f'\t{str(data)}'

    return callback_str


async def get_callback_data(data: str) -> CustomCallbackData:
    s = data.split('\t')[1:]
    return CustomCallbackData(
        operation_id=int(s[0]),
        sender_id=int(s[1])
    )
