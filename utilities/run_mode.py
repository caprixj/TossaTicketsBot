from enum import Enum


class RunMode(str, Enum):
    DEFAULT = 'default'
    DEV = 'dev'
    PROD = 'prod'


class RunModeSettings:
    def __init__(self,
                 bot_token: str = None,
                 group_chat_id: int = 0,
                 db_file_path: str = None):
        self.bot_token = bot_token
        self.group_chat_id = group_chat_id
        self.db_file_path = db_file_path
