from enum import Enum


class OverloadType(str, Enum):
    none = 'none'
    reply = 'reply'
    username = 'username'
    user_id = 'user_id'
