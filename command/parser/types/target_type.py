from enum import Enum


class CommandTargetType(str, Enum):
    NONE = 'none'
    REPLY = 'reply'
    USERNAME = 'username'
    USER_ID = 'user_id'
