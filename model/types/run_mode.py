from dataclasses import dataclass
from enum import Enum


class RunMode(str, Enum):
    DEFAULT = 'default'
    DEV = 'dev'
    PROD = 'prod'


@dataclass
class RunModeSettings:
    bot_token: str = None
    group_chat_id: int = 0
    db_backup_chat_id: int = 0
    db_file_path: str = None
