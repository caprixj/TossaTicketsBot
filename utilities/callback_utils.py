from typing import Optional


def generate_callback_data(name: str, *args) -> Optional[str]:
    data_list = list(args)
    callback_str = name

    for data in data_list:
        try:
            data_str = str(data)
            callback_str += f'\t{data_str}'
        except TypeError:
            return None

    return callback_str


async def get_callback_data(data: str) -> list[str]:
    return data.split('\t')[1:]
