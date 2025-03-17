from typing import Optional

from utilities.callback.tpay_callback_data import TpayCallbackData


def generate_callback_data(name: str, *args) -> Optional[str]:
    data_list = list(args)
    callback_str = name

    for data in data_list:
        callback_str += f'\t{str(data)}'

    return callback_str


async def get_callback_data(data: str) -> TpayCallbackData:
    s = data.split('\t')[1:]
    return TpayCallbackData(
        operation_id=int(s[0]),
        sender_id=int(s[1])
    )
