from enum import Enum


class CommandTargetType(str, Enum):
    none = 'none'
    reply = 'reply'
    username = 'username'
    user_id = 'operation_id'
