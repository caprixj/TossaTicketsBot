from dataclasses import dataclass, field
from typing import List


@dataclass
class ConfigChat:
    chat_id: int
    broadcast: bool


@dataclass
class RunModeSettings:
    bot_token: str = None
    host_url: str = None
    db_file_path: str = None
    admin_ids: List[int] = field(default_factory=list)
    main_chat: ConfigChat = None
    side_chats: List[ConfigChat] = field(default_factory=list)
    db_backup_chat_id: int = 0

    def get_admin_ids(self) -> list[int]:
        return self.admin_ids

    def is_admin(self, user_id: int) -> bool:
        return user_id in self.get_admin_ids()

    def get_chat_whitelist(self) -> list[ConfigChat]:
        return [self.main_chat, *self.side_chats]

    def get_broadcasting_chats(self) -> list[int]:
        return [
            chat.chat_id for chat in self.get_chat_whitelist()
            if chat.broadcast
        ]

    def is_whitelist_chat(self, chat_id: int) -> bool:
        return chat_id in [chat.chat_id for chat in self.get_chat_whitelist()]
