import re
from typing import Any, Optional, Type


def encode_cbdata(signature: str, data: dict[str, Any]) -> str:
    """
        only values are encoded, keys are dropped.
        dict is used only to enforce names for data values in code instead of using optional comments
    """
    contains_colon = any(
        ':' in str(value) for value in data.values()
        if value is not None
    )

    if contains_colon:
        raise ValueError('Callback data contains colon (:)')

    if not bool(re.match(r'^[^:\d]+:[^:\d]+:$', signature)):
        raise ValueError(f'Invalid callback signature: "{signature}" | (must be "msell:quantity:" e.g.)')

    encoded_data = ':'.join([str(val) for val in data.values()])
    return f'{signature}{encoded_data}'


def kdecode_cbdata(data: str, binding_keys: dict[str, Type]) -> dict[str, Any]:
    """
        example:
        data = kdecode_cbdata(
            data=callback.data,
            binding_keys={
                'sender_id': int,
                'operation_id': UUID,
            }
        )
    """
    data_list = data.split(':')
    if len(data_list) != len(binding_keys):
        raise ValueError('Callback data elements count and binding keys count do not match')

    result = {}
    for value, (name, of_type) in zip(data_list, binding_keys.items()):
        try:
            result[name] = of_type(value)
        except ValueError as e:
            raise ValueError(f"Could not cast a value [{value}] to a binding key's type [{of_type}]. details: {e}")

    return result


def ldecode_cbdata(data: str, binding_types: list[Type] = None) -> list:
    """
        example 1:
        a, b, c = ldecode_cbdata(
            data=callback.data,
            binding_types=[int, UUID, str]
        )

        example 2:
        a, = ldecode_cbdata(callback.data)
    """
    data_list = data.split(':')[2:]

    if not binding_types:
        return data_list

    if len(data_list) != len(binding_types):
        raise ValueError('Callback data elements count and binding types count do not match')

    result = []
    for value, of_type in zip(data_list, binding_types):
        try:
            result.append(of_type(value))
        except ValueError as e:
            raise ValueError(f"Could not cast a value [{value}] to a binding type [{of_type}]. details: {e}")

    return result


def encode_cbkey(key: str, signature: str) -> str:
    """
        keeping under telegram 64-byte limit
        key: <uuid4>
        signature: "<flow_name>:<action>:" (callback signature)
    """
    return f'{signature}{key}'


def decode_cbkey(data: str) -> Optional[str]:
    key = data.split(':')[2]
    if not key:
        raise ValueError('Callback data without a Redis key (uuid4)')
    return key
