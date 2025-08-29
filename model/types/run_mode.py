from dataclasses import dataclass, field
from enum import Enum
from typing import List


class RunMode(str, Enum):
    DEFAULT = 'default'
    DEV = 'dev'
    PROD = 'prod'


@dataclass
class RunModeSettings:
    bot_token: str = None
    host_url: str = None
    main_chat_id: int = 0
    side_chat_ids: List[int] = field(default_factory=list)
    db_backup_chat_id: int = 0
    db_file_path: str = None

    def get_allowed_chats(self) -> list[int]:
        return [self.main_chat_id, *self.side_chat_ids]

    def allowed_chat(self, chat_id: int) -> bool:
        return chat_id in self.get_allowed_chats()
